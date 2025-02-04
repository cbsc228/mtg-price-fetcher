# mtg-price-fetcher
MTG Price Fetcher is a Python script that uses Scryfall's API to fetch Magic: The Gathering card prices, process them, and upload them to a local price history database. Ideal for tracking price trends and analyzing market fluctuations over time.

The local database that this script is supporting is a MariaDB running on a RaspberryPi. Below are the commands for creating the database and tables as currently designed:

CREATE DATABASE `mtg_collection` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci */

-- mtg_collection.collections definition

CREATE TABLE `collections` (
  `collection_id` int(3) NOT NULL AUTO_INCREMENT,
  `collection_name` varchar(100) NOT NULL,
  PRIMARY KEY (`collection_id`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci COMMENT='All my different collections of cards ranging from binders to bulk to constructed decks';

-- mtg_collection.cards definition

CREATE TABLE `cards` (
  `scryfall_id` varchar(36) NOT NULL,
  `collection_id` int(11) NOT NULL,
  `name` varchar(141) NOT NULL,
  `set_code` varchar(5) NOT NULL,
  `foil` varchar(6) NOT NULL,
  `rarity` varchar(8) NOT NULL,
  `quantity` int(11) NOT NULL,
  `purchase_price` float NOT NULL,
  `misprint` tinyint(1) NOT NULL DEFAULT 0,
  `altered` tinyint(1) NOT NULL DEFAULT 0,
  `condition` varchar(20) NOT NULL,
  `language` varchar(5) NOT NULL,
  `purchase_price_currency` varchar(5) NOT NULL,
  `set_name` varchar(100) NOT NULL,
  PRIMARY KEY (`scryfall_id`,`collection_id`,`foil`),
  KEY `cards_collections_FK` (`collection_id`),
  CONSTRAINT `cards_collections_FK` FOREIGN KEY (`collection_id`) REFERENCES `collections` (`collection_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- mtg_collection.price_history definition

CREATE TABLE `price_history` (
  `scryfall_id` varchar(36) NOT NULL,
  `date` date NOT NULL,
  `usd` float DEFAULT NULL,
  `usd_foil` float DEFAULT NULL,
  `usd_etched` float DEFAULT NULL,
  `eur` float DEFAULT NULL,
  `eur_foil` float DEFAULT NULL,
  `tix` float DEFAULT NULL,
  PRIMARY KEY (`scryfall_id`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;
