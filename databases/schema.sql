create table mf_money (
    id serial primary key,
    category integer not null,
    money integer not null,
    note text,
    datetime date not null default 'now',
    created timestamp not null default 'now'
);

create table mf_category (
  id serial primary key,
  category varchar(45) not null
);

insert into mf_category (category) values ('食費');
insert into mf_category (category) values ('交通費');
insert into mf_category (category) values ('雑貨費');
insert into mf_category (category) values ('書籍費');
insert into mf_category (category) values ('娯楽費');
insert into mf_category (category) values ('被服費');
insert into mf_category (category) values ('定期的支払い料金');
