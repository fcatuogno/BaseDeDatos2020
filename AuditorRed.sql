
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
    `EdificioID` INT NOT NULL AUTO_INCREMENT,
    `Nombre` NVARCHAR(25),
    `Direccion` NVARCHAR(50),
    CONSTRAINT `PK_Edificio` PRIMARY KEY  (`EdificioID`),
    CONSTRAINT `UNIQUE_NombreDireccion` UNIQUE (`Nombre`, `Direccion`)
);

CREATE TABLE `Tablero`
(
    `TableroID` INT NOT NULL AUTO_INCREMENT,
    `Nombre` NVARCHAR(25) ,
	`EdificioID` INT NOT NULL,
    CONSTRAINT `PK_Tablero` PRIMARY KEY  (`TableroID`),
    CONSTRAINT `UNIQUE_TableroEdificio` UNIQUE (`Nombre`, `EdificioID`)
);

CREATE TABLE `Linea`
(
    `LineaID` INT NOT NULL AUTO_INCREMENT,
    `Nombre` NVARCHAR(25),
    `TableroID` INT NOT NULL,	
    CONSTRAINT `PK_Linea` PRIMARY KEY  (`LineaID`),
    CONSTRAINT `UNIQUE_LineaTablero` UNIQUE (`Nombre`, `TableroID`)
);

CREATE TABLE `Unidad`
(
    `UnidadID` INT NOT NULL AUTO_INCREMENT,
    `Unidad` NVARCHAR(25) UNIQUE,

    CONSTRAINT `PK_Unidad` PRIMARY KEY  (`UnidadID`)
);

CREATE TABLE `Medicion`
(
    `MedicionID` INT NOT NULL AUTO_INCREMENT,
    `Nombre` NVARCHAR(25),
    `LineaID` INT NOT NULL,
    `UnidadID` INT NOT NULL,
    `Intervalo` INT NOT NULL DEFAULT 5,

    CONSTRAINT `PK_Medicion` PRIMARY KEY  (`MedicionID`),
    CONSTRAINT `UNIQUE_LineaUnidad` UNIQUE (`LineaID`, `UnidadID`)
);

CREATE TABLE `ValorMedicion`
(
    `ValorMedicionID` INT NOT NULL AUTO_INCREMENT,
    `Valor` NUMERIC(10,2),
    `UnixTimeStamp` INT,
    `MedicionID` INT NOT NULL,
    
    CONSTRAINT `PK_ValorMedicion` PRIMARY KEY  (`ValorMedicionID`)
);

CREATE TABLE `Umbral`
(
    `UmbralID` INT NOT NULL AUTO_INCREMENT,
    `MedicionID` INT NOT NULL,
    `Severidad` ENUM('leve', 'grave', 'critico'),

    `UmbralInferior` NUMERIC(10,2),
    `UmbralSuperior` NUMERIC(10,2),
     
    CONSTRAINT `PK_Umbral` PRIMARY KEY (`UmbralID`),
    CONSTRAINT `UNIQUE_MedicionSeveridadUmbralInferior` UNIQUE (`MedicionID`, `Severidad`, `UmbralInferior`),
    CONSTRAINT `UNIQUE_MedicionSeveridadUmbralSuperior` UNIQUE (`MedicionID`, `Severidad`, `UmbralSuperior`)

);

CREATE TABLE `Alarma`
(
    `AlarmaID` INT NOT NULL AUTO_INCREMENT,
    `UmbralID` INT NOT NULL,
    `ValorMedicionID` INT NOT NULL,    
    CONSTRAINT `PK_Alarmas` PRIMARY KEY (`AlarmaID`)
);


/*******************************************************************************
   Create Primary Key Unique Indexes
********************************************************************************/

/*******************************************************************************
   Create Foreign Keys
********************************************************************************/
ALTER TABLE `Tablero` ADD CONSTRAINT `FK_TableroEdificioID`
    FOREIGN KEY (`EdificioID`) REFERENCES `Edificio` (`EdificioID`) 
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE `Linea` ADD CONSTRAINT `FK_LineaTableroID`
    FOREIGN KEY (`TableroID`) REFERENCES `Tablero` (`TableroID`) 
    ON UPDATE CASCADE
    ON DELETE CASCADE;

ALTER TABLE `Medicion` ADD CONSTRAINT `FK_MedicionUnidadID`
    FOREIGN KEY (`UnidadID`) REFERENCES `Unidad` (`UnidadID`) 
    ON UPDATE NO ACTION
    ON DELETE NO ACTION;

ALTER TABLE `Medicion` ADD CONSTRAINT `FK_MedicionLineaID`
    FOREIGN KEY (`LineaID`) REFERENCES `Linea` (`LineaID`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `ValorMedicion` ADD CONSTRAINT `FK_ValorMedicionMedicionID`
    FOREIGN KEY (`MedicionID`) REFERENCES `Medicion` (`MedicionID`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Umbral` ADD CONSTRAINT `FK_UmbralMedicionID`
    FOREIGN KEY (`MedicionID`) REFERENCES `Medicion` (`MedicionID`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Alarma` ADD CONSTRAINT `FK_AlarmaUmbralID`
    FOREIGN KEY (`UmbralID`) REFERENCES `Umbral` (`UmbralID`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;

ALTER TABLE `Alarma` ADD CONSTRAINT `FK_AlarmaValorMedicionID`
    FOREIGN KEY (`ValorMedicionID`) REFERENCES `ValorMedicion` (`ValorMedicionID`) 
	ON DELETE  CASCADE
	ON UPDATE  CASCADE;