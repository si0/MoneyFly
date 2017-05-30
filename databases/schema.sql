create table moneyfly (
    id serial primary key,
    title varchar(45) not null,
    money integer not null,
    note text,
    datetime date not null default 'now',
    created timestamp not null default 'now'
);
