begin;

create schema mdb;

create user mdb;

grant usage on schema to mdb;

create type date_precision as enum ('d', 'm', 'y');

create table mdb.country
(
    id              serial primary key,
    name            text not null unique
);

grant select, insert on table mdb.country to mdb;

create table mdb.movie
(
    id              serial primary key,
    title           text not null,
    alternative_title text,
    countries       integer[],
    year            integer not null,
    slogan          text,
    directors       integer[],
    scenario        integer[],
    operators       integer[],
    composers       integer[],
    producers       integer[],
    arts            integer[],
    editors         integer[],
    genres          integer[],
    length          integer,
    age_restriction text,
    rating_imdb     numeric,
    rating_kinopoisk numeric,
    rating_critics  numeric,
    world_premiere  date,
    parse_date      timestamptz(0) not null default now()
);

create table mdb.movie_boxes
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    category        text not null,
    item            text not null,
    value           bigint,
    currency        varchar(100)
);

comment on table mdb.movie_boxes is 'Сборы';

grant select, usage on sequence mdb.movie_boxes_id_seq to mdb;
grant select, insert, update, delete on mdb.movie_boxes to mdb;

create index on mdb.movie_boxes (movie_id);

create table mdb.rating_history
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    day             date not null,
    rating          numeric not null
);

comment on table mdb.rating_history is 'Динамика изменения рейтинга фильма';

create table mdb.country_views
(
    id              serial primary key,
    country_id      integer not null references mdb.country(id),
    movie_id        integer not null references mdb.movie(id),
    views           integer not null check (views > 0)
);

create table mdb.premiere_date
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    region          varchar(100) not null,
    premiere_date   date,
    precision       date_precision not null default 'd',
    commentary      text
);

create unique index on mdb.premiere_date(movie_id, region);

grant select, usage on sequence mdb.premiere_date_id_seq to mdb;
grant select, insert, update on mdb.premiere_date to mdb;

create table mdb.genre
(
    id              serial primary key,
    name            text not null unique
);

grant insert, update, select on mdb.genre to mdb;

create table mdb.movie_keyword
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    keyword         text not null
);

create unique index on mdb.movie_keyword (movie_id, keyword);

create table mdb.person
(
    id              serial primary key,
    name            text not null,
    alternative_name text
);

create table mdb.person_in_movie
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    person_id       integer not null references mdb.person(id),
    role            text not null,
    commentary      text
);

create index on mdb.person_in_movie(movie_id);
create index on mdb.person_in_movie(person_id);

grant select, update, delete, insert on table mdb.person, mdb.person_in_movie to mdb;

grant select, usage on sequence mdb.person_in_movie_id_seq to mdb;

create table mdb.movie_rating
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    rating_system   varchar(100) not null,
    rating          numeric not null,
    vote_count      integer
);

grant insert, update, delete, select on mdb.movie_rating to mdb;
grant select, usage on sequence mdb.movie_rating_id_seq to mdb;

create unique index on mdb.movie_rating(movie_id, rating_system);

create table mdb.stat
(
    id              serial primary key,
    year            integer not null unique,
    done_count      integer not null default 0 check (done_count >= 0),
    total_count     integer not null check (total_count >= 0),
    last_update_time timestamptz(0) not null default now()
);

grant select, update, insert on mdb.stat to mdb;
grant select, usage on sequence mdb.stat_id_seq to mdb;

create table mdb.dates
(
    id              serial primary key,
    movie_id        integer not null references mdb.movie(id),
    country_id      integer not null references mdb.country(id),
    premiere_date   date,
    premiere_precision char(1),
    viewers         integer,
    commentary      text
);

create index on mdb.dates (movie_id);

grant select, insert, update, delete on mdb.dates to mdb;
grant select, usage on sequence mdb.dates_id_seq to mdb;

end;