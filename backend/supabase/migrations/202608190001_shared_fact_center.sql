begin;

create extension if not exists pgcrypto;

create table public.organizations (
  id uuid primary key default gen_random_uuid(),
  slug text not null unique check (slug ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  name text not null check (length(btrim(name)) between 1 and 120),
  created_at timestamptz not null default now()
);

create table public.organization_members (
  organization_id uuid not null references public.organizations(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  member_id text not null check (member_id ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  display_name text not null check (length(btrim(display_name)) between 1 and 120),
  role text not null check (role in ('owner', 'manager', 'member')),
  active boolean not null default true,
  created_at timestamptz not null default now(),
  primary key (organization_id, user_id),
  unique (organization_id, member_id)
);

create function public.is_active_org_member(p_organization_id uuid, p_user_id uuid default auth.uid())
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.organization_members m
    where m.organization_id = p_organization_id
      and m.user_id = p_user_id
      and m.active
  );
$$;

create function public.is_org_manager(p_organization_id uuid, p_user_id uuid default auth.uid())
returns boolean
language sql
stable
security definer
set search_path = public
as $$
  select exists (
    select 1
    from public.organization_members m
    where m.organization_id = p_organization_id
      and m.user_id = p_user_id
      and m.active
      and m.role in ('owner', 'manager')
  );
$$;

revoke all on function public.is_active_org_member(uuid, uuid) from public;
revoke all on function public.is_org_manager(uuid, uuid) from public;
grant execute on function public.is_active_org_member(uuid, uuid) to authenticated;
grant execute on function public.is_org_manager(uuid, uuid) to authenticated;

create function public.assert_coordination_safe(p_value text, p_field text)
returns void
language plpgsql
immutable
set search_path = public
as $$
begin
  if p_value is null or length(btrim(p_value)) = 0 then
    raise exception '% must be non-empty', p_field using errcode = '22023';
  end if;
  if p_value ~* 'https?://' then
    raise exception '% contains a prohibited URL', p_field using errcode = '22023';
  end if;
  if p_value ~* 'file://' then
    raise exception '% contains a prohibited local URL', p_field using errcode = '22023';
  end if;
  if p_value ~ '(?:^|[[:space:]])/(Users|home|Volumes)/' then
    raise exception '% contains a prohibited local path', p_field using errcode = '22023';
  end if;
  if p_value ~ '[A-Za-z]:[\\/]' then
    raise exception '% contains a prohibited Windows path', p_field using errcode = '22023';
  end if;
  if p_value ~ '\\\\[^\\[:space:]]+\\' then
    raise exception '% contains a prohibited network path', p_field using errcode = '22023';
  end if;
  if p_value ~* '(api[_-]?key|access[_-]?token|secret)[[:space:]]*[:=]' then
    raise exception '% contains a prohibited credential pattern', p_field using errcode = '22023';
  end if;
  if p_value ~ '-----BEGIN [A-Z ]*PRIVATE KEY-----' then
    raise exception '% contains a prohibited private key', p_field using errcode = '22023';
  end if;
  if p_value ~ 'gh[opstu]_[A-Za-z0-9]{10,}' then
    raise exception '% contains a prohibited GitHub token', p_field using errcode = '22023';
  end if;
end;
$$;

revoke all on function public.assert_coordination_safe(text, text) from public;

create table public.tasks (
  id uuid primary key default gen_random_uuid(),
  organization_id uuid not null references public.organizations(id) on delete cascade,
  external_id text not null check (external_id ~ '^[a-z0-9]+(?:-[a-z0-9]+)*$'),
  title text not null check (length(title) between 1 and 160),
  assigner_user_id uuid not null references auth.users(id),
  assignee_user_id uuid not null references auth.users(id),
  project_id text not null default 'none' check (length(project_id) between 1 and 64),
  safe_context text not null check (length(safe_context) between 1 and 500),
  priority text not null check (priority in ('high', 'medium', 'low')),
  status text not null default 'assigned' check (status in ('assigned', 'accepted', 'in_progress', 'waiting', 'done', 'declined')),
  health text not null default 'yellow' check (health in ('red', 'yellow', 'green')),
  status_reason text not null check (length(status_reason) between 1 and 500),
  due timestamptz,
  next_action text not null check (length(next_action) between 1 and 500),
  blocker text not null default 'none' check (length(blocker) between 1 and 500),
  done_criteria text not null check (length(done_criteria) between 1 and 500),
  check_date date,
  source_reference text not null default 'none' check (source_reference ~ '^(none|[A-Za-z0-9][A-Za-z0-9._-]{0,63})$'),
  safe_evidence text not null default 'none' check (length(safe_evidence) between 1 and 500),
  confidentiality text not null default 'coordination_only' check (confidentiality = 'coordination_only'),
  revision integer not null default 1 check (revision > 0),
  pushed_at timestamptz not null default now(),
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  updated_by_user_id uuid not null references auth.users(id),
  unique (organization_id, external_id)
);

create function public.validate_coordination_task()
returns trigger
language plpgsql
set search_path = public
as $$
declare
  v_field text;
  v_value text;
begin
  for v_field, v_value in
    select * from (values
      ('title', new.title),
      ('project_id', new.project_id),
      ('safe_context', new.safe_context),
      ('status_reason', new.status_reason),
      ('next_action', new.next_action),
      ('blocker', new.blocker),
      ('done_criteria', new.done_criteria),
      ('source_reference', new.source_reference),
      ('safe_evidence', new.safe_evidence)
    ) as fields(field_name, field_value)
  loop
    perform public.assert_coordination_safe(v_value, v_field);
  end loop;

  if not public.is_active_org_member(new.organization_id, new.assigner_user_id)
     or not public.is_active_org_member(new.organization_id, new.assignee_user_id)
     or not public.is_active_org_member(new.organization_id, new.updated_by_user_id) then
    raise exception 'task references a user outside the organization' using errcode = '42501';
  end if;

  if new.status = 'done' and new.safe_evidence = 'none' then
    raise exception 'done tasks require reviewed safe evidence' using errcode = '22023';
  end if;

  if new.status = 'done' and new.completed_at is null then
    new.completed_at := now();
  elsif new.status <> 'done' then
    new.completed_at := null;
  end if;
  return new;
end;
$$;

create trigger tasks_validate_before_write
before insert or update on public.tasks
for each row execute function public.validate_coordination_task();

create table public.task_receipts (
  task_id uuid not null references public.tasks(id) on delete cascade,
  user_id uuid not null references auth.users(id) on delete cascade,
  pushed_at timestamptz not null default now(),
  read_at timestamptz,
  accepted_at timestamptz,
  completed_at timestamptz,
  last_seen_revision integer not null default 0 check (last_seen_revision >= 0),
  primary key (task_id, user_id)
);

create table public.task_events (
  id bigint generated always as identity primary key,
  organization_id uuid not null references public.organizations(id) on delete cascade,
  task_id uuid not null references public.tasks(id) on delete cascade,
  actor_user_id uuid not null references auth.users(id),
  event_type text not null check (event_type in ('pushed', 'read', 'accepted', 'status_changed', 'completed', 'declined')),
  from_status text,
  to_status text,
  safe_summary text not null default 'none',
  task_revision integer not null check (task_revision > 0),
  created_at timestamptz not null default now()
);

create function public.audit_task_write()
returns trigger
language plpgsql
security definer
set search_path = public
as $$
declare
  v_event_type text;
begin
  if tg_op = 'INSERT' then
    v_event_type := 'pushed';
  elsif new.status = old.status then
    return new;
  elsif new.status = 'done' then
    v_event_type := 'completed';
  elsif new.status = 'accepted' then
    v_event_type := 'accepted';
  elsif new.status = 'declined' then
    v_event_type := 'declined';
  else
    v_event_type := 'status_changed';
  end if;

  insert into public.task_events (
    organization_id, task_id, actor_user_id, event_type, from_status,
    to_status, safe_summary, task_revision
  ) values (
    new.organization_id, new.id, new.updated_by_user_id, v_event_type,
    case when tg_op = 'UPDATE' then old.status else null end,
    new.status, new.status_reason, new.revision
  );
  return new;
end;
$$;

create trigger tasks_audit_after_write
after insert or update on public.tasks
for each row execute function public.audit_task_write();

alter table public.organizations enable row level security;
alter table public.organization_members enable row level security;
alter table public.tasks enable row level security;
alter table public.task_receipts enable row level security;
alter table public.task_events enable row level security;

create policy organizations_select_member on public.organizations
for select to authenticated
using (public.is_active_org_member(id));

create policy members_select_member on public.organization_members
for select to authenticated
using (public.is_active_org_member(organization_id));

create policy members_manage_manager on public.organization_members
for all to authenticated
using (public.is_org_manager(organization_id))
with check (public.is_org_manager(organization_id));

create policy tasks_select_participant on public.tasks
for select to authenticated
using (
  public.is_active_org_member(organization_id)
  and (
    public.is_org_manager(organization_id)
    or assigner_user_id = auth.uid()
    or assignee_user_id = auth.uid()
  )
);

create policy tasks_insert_manager on public.tasks
for insert to authenticated
with check (
  public.is_org_manager(organization_id)
  and assigner_user_id = auth.uid()
  and updated_by_user_id = auth.uid()
);

create policy receipts_select_member on public.task_receipts
for select to authenticated
using (
  exists (
    select 1 from public.tasks t
    where t.id = task_id
      and public.is_active_org_member(t.organization_id)
      and (task_receipts.user_id = auth.uid() or public.is_org_manager(t.organization_id))
  )
);

create policy events_select_participant on public.task_events
for select to authenticated
using (
  exists (
    select 1 from public.tasks t
    where t.id = task_id
      and (
        public.is_org_manager(t.organization_id)
        or t.assigner_user_id = auth.uid()
        or t.assignee_user_id = auth.uid()
      )
  )
);

grant select on public.organizations, public.organization_members, public.tasks,
  public.task_receipts, public.task_events to authenticated;
grant insert, update, delete on public.organization_members to authenticated;
grant insert on public.tasks to authenticated;
revoke update, delete on public.tasks from authenticated;
revoke insert, update, delete on public.task_events from authenticated;
revoke insert, update, delete on public.task_receipts from authenticated;

create function public.mark_task_read(
  p_task_id uuid,
  p_expected_revision integer,
  p_confirm boolean
)
returns public.task_receipts
language plpgsql
security definer
set search_path = public
as $$
declare
  v_task public.tasks;
  v_receipt public.task_receipts;
begin
  if p_confirm is not true then
    raise exception 'explicit confirmation is required' using errcode = '42501';
  end if;
  select * into v_task from public.tasks where id = p_task_id;
  if not found or v_task.assignee_user_id <> auth.uid() then
    raise exception 'task is not assigned to the current user' using errcode = '42501';
  end if;
  if v_task.revision <> p_expected_revision then
    raise exception 'task revision changed; review the full envelope again' using errcode = '40001';
  end if;

  insert into public.task_receipts (task_id, user_id, pushed_at, read_at, last_seen_revision)
  values (v_task.id, auth.uid(), v_task.pushed_at, now(), v_task.revision)
  on conflict (task_id, user_id) do update
    set read_at = coalesce(task_receipts.read_at, excluded.read_at),
        last_seen_revision = excluded.last_seen_revision
  returning * into v_receipt;

  insert into public.task_events (
    organization_id, task_id, actor_user_id, event_type, from_status,
    to_status, safe_summary, task_revision
  ) values (
    v_task.organization_id, v_task.id, auth.uid(), 'read', v_task.status,
    v_task.status, 'Envelope explicitly reviewed', v_task.revision
  );
  return v_receipt;
end;
$$;

create function public.update_task_status(
  p_task_id uuid,
  p_expected_revision integer,
  p_status text,
  p_health text,
  p_status_reason text,
  p_next_action text,
  p_blocker text,
  p_safe_evidence text,
  p_confirm boolean
)
returns public.tasks
language plpgsql
security definer
set search_path = public
as $$
declare
  v_task public.tasks;
  v_result public.tasks;
begin
  if p_confirm is not true then
    raise exception 'explicit confirmation is required' using errcode = '42501';
  end if;
  select * into v_task from public.tasks where id = p_task_id for update;
  if not found or (v_task.assignee_user_id <> auth.uid() and not public.is_org_manager(v_task.organization_id)) then
    raise exception 'task cannot be updated by the current user' using errcode = '42501';
  end if;
  if v_task.revision <> p_expected_revision then
    raise exception 'task revision changed; review the full envelope again' using errcode = '40001';
  end if;
  if p_status not in ('accepted', 'in_progress', 'waiting', 'done', 'declined') then
    raise exception 'invalid outbound status' using errcode = '22023';
  end if;
  if p_health not in ('red', 'yellow', 'green') then
    raise exception 'invalid health' using errcode = '22023';
  end if;

  update public.tasks
  set status = p_status,
      health = p_health,
      status_reason = p_status_reason,
      next_action = p_next_action,
      blocker = p_blocker,
      safe_evidence = p_safe_evidence,
      revision = revision + 1,
      updated_at = now(),
      updated_by_user_id = auth.uid()
  where id = p_task_id
  returning * into v_result;

  insert into public.task_receipts (
    task_id, user_id, pushed_at, read_at, accepted_at, completed_at,
    last_seen_revision
  ) values (
    v_result.id, auth.uid(), v_result.pushed_at, now(),
    case when p_status in ('accepted', 'in_progress', 'waiting', 'done') then now() end,
    case when p_status = 'done' then now() end,
    v_result.revision
  ) on conflict (task_id, user_id) do update
    set read_at = coalesce(task_receipts.read_at, excluded.read_at),
        accepted_at = coalesce(task_receipts.accepted_at, excluded.accepted_at),
        completed_at = coalesce(task_receipts.completed_at, excluded.completed_at),
        last_seen_revision = excluded.last_seen_revision;
  return v_result;
end;
$$;

revoke all on function public.mark_task_read(uuid, integer, boolean) from public;
revoke all on function public.update_task_status(uuid, integer, text, text, text, text, text, text, boolean) from public;
grant execute on function public.mark_task_read(uuid, integer, boolean) to authenticated;
grant execute on function public.update_task_status(uuid, integer, text, text, text, text, text, text, boolean) to authenticated;

create view public.task_envelopes
with (security_invoker = true)
as
select
  1::integer as schema_version,
  t.external_id as id,
  t.title,
  assigner.member_id as assigner_id,
  assignee.member_id as assignee_id,
  t.project_id,
  t.safe_context,
  t.priority,
  t.status,
  t.health,
  t.status_reason,
  coalesce(to_char(t.due at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'), 'TBD') as due,
  t.next_action,
  t.blocker,
  t.done_criteria,
  coalesce(t.check_date::text, 'TBD') as check_date,
  t.source_reference,
  t.safe_evidence,
  t.confidentiality,
  t.revision,
  to_char(t.updated_at at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"') as updated_at,
  updater.member_id as updated_by
from public.tasks t
join public.organization_members assigner
  on assigner.organization_id = t.organization_id and assigner.user_id = t.assigner_user_id
join public.organization_members assignee
  on assignee.organization_id = t.organization_id and assignee.user_id = t.assignee_user_id
join public.organization_members updater
  on updater.organization_id = t.organization_id and updater.user_id = t.updated_by_user_id;

grant select on public.task_envelopes to authenticated;

commit;
