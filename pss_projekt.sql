create database test_pss;
use test_pss;

create table users(
id int primary key identity (1,1),
jmeno varchar(100) not null unique,
cardUID varchar(100) not null unique
);

create table prichody(
id int primary key identity (1,1),
users_id int not null foreign key references users(id),
cas datetime not null default getdate(),
typ varchar(10) not null
);

INSERT INTO users (jmeno, cardUID) VALUES ('Adam', '04E15A63320289');
INSERT INTO users (jmeno, cardUID) VALUES ('Filip', '1234567890AB');
INSERT INTO users (jmeno, cardUID) VALUES ('Cyril', 'D759C431');

select * from users;
select * from prichody;

SELECT *
FROM prichody
WHERE users_id = 4
ORDER BY cas DESC;

ALTER TABLE users
ADD CONSTRAINT UQ_users_jmeno UNIQUE (jmeno);

--SMAZÁNÍ KARTY PODLE ID, NAJDI SI POMOCÍ SELECTU ID, KTERÉ CHCEŠ SMAZAT (v pøípadì ztráty karty..)

select * from users;

-- OZNAÈ ØÁDKY POD TÍMHLE > F5/EXECUTE

DECLARE @id INT = 3; -- ZADEJ ID KARTY, KTEROU CHCEŠ SMAZAT

DELETE FROM prichody WHERE users_id = @id;
DELETE FROM users WHERE id = @id;