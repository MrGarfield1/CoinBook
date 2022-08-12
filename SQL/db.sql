CREATE DATABASE Монеты 
GO
USE Монеты

CREATE TABLE [Пользователи]
(
	[ИДПользователя]   integer NOT NULL IDENTITY(1,1) PRIMARY KEY,
	[Имя]              nvarchar(15) NOT NULL UNIQUE,
	[Email]            nvarchar(15) NOT NULL UNIQUE,
	[Пароль]           nvarchar(15) NOT NULL)

CREATE TABLE [Монеты]
(
	[ИДМонеты]         integer NOT NULL IDENTITY(1,1) PRIMARY KEY,
	[ИДПользователя]   integer NOT NULL,
	[Название]         nvarchar(30) NOT NULL,
	[Страна]           nvarchar(30) NOT NULL,
	[Год]              integer NOT NULL,
	[Тираж]            integer NOT NULL,
	[Материал]         nvarchar(50) NOT NULL,
	[Диаметр]          integer NOT NULL,
	[Цена]             integer NOT NULL,
	[Описание]         nvarchar(1000) NOT NULL,
	[Фото]             nvarchar(60) NOT NULL,
	CONSTRAINT [Пользователи_Монеты] FOREIGN KEY ([ИДПользователя]) REFERENCES [Пользователи]([ИДПользователя]) ON DELETE NO ACTION ON UPDATE NO ACTION) 
