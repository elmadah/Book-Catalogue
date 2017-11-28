drop table if exists BookCatalogue;
create table BookCatalogue (
    id integer primary key AUTO_INCREMENT,
    user_id integer not null,
    title varchar(200) not null,
    author varchar(200) not null,
    page_count varchar(200) not null,
    average_rating varchar(200) not null
);

drop table if exists Users;
create table Users (
    id integer primary key  AUTO_INCREMENT,
    username varchar(200) not null,
    password varchar(200) not null
);
insert into Users (username, password) values ('admin', 'admin');