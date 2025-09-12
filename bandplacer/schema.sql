drop table if exists user;
drop table if exists scores;

create table user(
       id integer primary key autoincrement,
       username text unique not null,
       password text not null,
       email text not null
);

create table scores(
       userid INT,
       method text,
       scores text,
       primary key (userid, method)
);

