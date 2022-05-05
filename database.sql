create database project14;
use project14;

create table users
(
    id int not null auto_increment primary key,
    fullname varchar(150) not null,
    email varchar(150) not null unique,
    password varchar(200) not null
);

create table articles
(
    id int not null auto_increment primary key,
    title varchar(400) not null,
    post text(5000) not null,
    likes int(10) default 0,
    dislikes int(10) default 0,
    userid int,
    foreign key (userid) references users(id)
);

create table friends
(
    id1 int,
    fid int,
    primary key (id1,fid),
    foreign key (id1) references users(id),
    foreign key (fid) references users(id)
);