
/*******************************************************************************
   AuditorRed Database - Version 1.0
   Script: AuditorRed_MySql.sql
   Description: Creates AuditorRed database.
   DB Server: MySql
   Author: Fabian Catuogno
   License: 
********************************************************************************/

/*******************************************************************************
   Drop database if it exists
********************************************************************************/
DROP DATABASE IF EXISTS `AuditorRed`;

/*******************************************************************************
   Create database
********************************************************************************/
CREATE DATABASE `AuditorRed`;

USE AuditorRed;

/*******************************************************************************
   Create Tables
********************************************************************************/
CREATE TABLE `Edificio`
(
    `EdificioId` INT NOT NULL,
    `Nombre` NVARCHAR(25),
    `Direccion` NVARCHAR(50),
    CONSTRAINT `PK_Edificio` PRIMARY KEY  (`EdificioId`)
);

CREATE TABLE `Tablero`
(
    `TableroId` INT NOT NULL,
    `Nombre` NVARCHAR(25) ,
	`EdificioId` INT NOT NULL,
    CONSTRAINT `PK_Tablero` PRIMARY KEY  (`TableroId`)
);

CREATE TABLE `Linea`
(
    `LineaId` INT NOT NULL,
    `Nombre` NVARCHAR(25),
    `TableroId` INT NOT NULL,	
    CONSTRAINT `PK_Linea` PRIMARY KEY  (`LineaId`)
);

CREATE TABLE `Unidad`
(
    `UnidadId` INT NOT NULL,
    `Unidad` NVARCHAR(25),

    CONSTRAINT `PK_Unidad` PRIMARY KEY  (`UnidadId`)
);

CREATE TABLE `Medicion`
(
    `MedicionId` INT NOT NULL,
    `LineaId` INT NOT NULL,
    `UnidadId` INT NOT NULL,
    `Intervalo` INT NOT NULL,

    CONSTRAINT `PK_Medicion` PRIMARY KEY  (`MedicionId`)
);

CREATE TABLE `ValorMedicion`
(
    `ValorId` INT NOT NULL,
    `Valor` NUMERIC(10,2),
    `UnixTimeStamp` INT,
    `MedicionId` INT NOT NULL,
    
    CONSTRAINT `PK_ValorMedicion` PRIMARY KEY  (`ValorID`)
);

CREATE TABLE `Umbral`
(
    `UmbralId` INT NOT NULL,
    `UnidadId` INT NOT NULL,
    `Severidad` ENUM('leve', 'grave', 'critico'),

    `Umbral_Inferior` NUMERIC(10,2),
    `Umbral_Superior` NUMERIC(10,2),
     
    CONSTRAINT `PK_Umbral` PRIMARY KEY (`UmbralID`)
);

CREATE TABLE `Alarma`
(
    `AlarmaID` INT NOT NULL,
    `UmbralID` INT NOT NULL,
    `ValorID` INT NOT NULL,    
    CONSTRAINT `PK_Alarmas` PRIMARY KEY (`AlarmaID`)
);


/*******************************************************************************
   Create Primary Key Unique Indexes
********************************************************************************/

/*******************************************************************************
   Create Foreign Keys
********************************************************************************/
ALTER TABLE `Tablero` ADD CONSTRAINT `FK_TableroEdificioId`
    FOREIGN KEY (`EdificioId`) REFERENCES `Edificio` (`EdificioId`) 
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE `Linea` ADD CONSTRAINT `FK_LineaTableroId`
    FOREIGN KEY (`TableroId`) REFERENCES `Tablero` (`TableroId`) 
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE `Medicion` ADD CONSTRAINT `FK_MedicionUnidadId`
    FOREIGN KEY (`UnidadId`) REFERENCES `Unidad` (`UnidadId`) 
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE `Medicion` ADD CONSTRAINT `FK_MedicionLineaId`
    FOREIGN KEY (`LineaId`) REFERENCES `Linea` (`LineaId`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `ValorMedicion` ADD CONSTRAINT `FK_ValorMedicioMedicionId`
    FOREIGN KEY (`MedicionId`) REFERENCES `Medicion` (`MedicionId`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Umbral` ADD CONSTRAINT `FK_UmbralUnidadId`
    FOREIGN KEY (`UnidadId`) REFERENCES `Unidad` (`UnidadId`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Alarma` ADD CONSTRAINT `FK_AlarmaUmbralId`
    FOREIGN KEY (`UmbralId`) REFERENCES `Umbral` (`UmbralId`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Alarma` ADD CONSTRAINT `FK_AlarmaValorId`
    FOREIGN KEY (`ValorId`) REFERENCES `ValorMedicion` (`ValorId`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;