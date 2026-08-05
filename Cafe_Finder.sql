/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19-11.8.5-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: Cafe_Finder
-- ------------------------------------------------------
-- Server version	11.8.5-MariaDB-4 from Debian

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*M!100616 SET @OLD_NOTE_VERBOSITY=@@NOTE_VERBOSITY, NOTE_VERBOSITY=0 */;

--
-- Table structure for table `admins`
--

DROP TABLE IF EXISTS `admins`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `admins` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `email` varchar(100) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `admins`
--

LOCK TABLES `admins` WRITE;
/*!40000 ALTER TABLE `admins` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `admins` VALUES
(1,'admin@gmail.com','scrypt:32768:8:1$0kLoSssEn594t1fs$b5de5efe0a9f9aea1dad7af44ece6308ecba553509b3b7a20f3c375972c843676bd908c35965acfb68f135034264691234f58ca75b32ce0689ef7534f36978fb');
/*!40000 ALTER TABLE `admins` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `cafe_images`
--

DROP TABLE IF EXISTS `cafe_images`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cafe_images` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cafe_id` int(11) NOT NULL,
  `image_path` varchar(255) NOT NULL,
  `uploaded_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `fk_images_cafe` (`cafe_id`),
  CONSTRAINT `cafe_images_ibfk_1` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `fk_images_cafe` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cafe_images`
--

LOCK TABLES `cafe_images` WRITE;
/*!40000 ALTER TABLE `cafe_images` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `cafe_images` VALUES
(12,12,'uploads/tea_garden_and_co_1.jpg','2026-07-30 22:26:21'),
(13,12,'uploads/tea_garden_and_co_2.webp','2026-07-30 22:26:21'),
(14,12,'uploads/tea_garden_and_co_3.webp','2026-07-30 22:26:21');
/*!40000 ALTER TABLE `cafe_images` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `cafes`
--

DROP TABLE IF EXISTS `cafes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `cafes` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `location` varchar(255) DEFAULT NULL,
  `open_time` time DEFAULT NULL,
  `close_time` time DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `average_rating` decimal(3,2) DEFAULT 0.00,
  `status` enum('open','closed') DEFAULT 'open',
  `latitude` decimal(10,8) DEFAULT NULL,
  `longitude` decimal(11,8) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`),
  KEY `idx_cafe_location` (`location`)
) ENGINE=InnoDB AUTO_INCREMENT=15 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cafes`
--

LOCK TABLES `cafes` WRITE;
/*!40000 ALTER TABLE `cafes` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `cafes` VALUES
(12,'Tea garden and co','A cozy and elegant cafe that offers a relaxing environment where guests can enjoy a variety of refreshing teas, coffee, snacks, and delicious food. With a peaceful garden-inspired atmosphere, comfortable seating, and friendly service, it is a perfect place to spend quality time with friends, family, or colleagues. The cafe serves a blend of traditional and modern beverages along with tasty snacks and desserts, creating a warm and memorable dining experience for every visitor','Aitabare Path, Itahari','08:00:00','21:00:00','2026-07-30 22:26:21',0.00,'open',NULL,NULL);
/*!40000 ALTER TABLE `cafes` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `menu_items`
--

DROP TABLE IF EXISTS `menu_items`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `menu_items` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cafe_id` int(11) NOT NULL,
  `item_name` varchar(100) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `price` decimal(10,2) NOT NULL,
  `available` tinyint(1) DEFAULT 1,
  PRIMARY KEY (`id`),
  UNIQUE KEY `cafe_id` (`cafe_id`,`item_name`),
  KEY `idx_menu_price` (`price`),
  CONSTRAINT `fk_menu_cafe` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `chk_price` CHECK (`price` > 0)
) ENGINE=InnoDB AUTO_INCREMENT=108 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `menu_items`
--

LOCK TABLES `menu_items` WRITE;
/*!40000 ALTER TABLE `menu_items` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `menu_items` VALUES
(80,12,'Masala Tea',NULL,80.00,1),
(81,12,'Milk Tea',NULL,60.00,1),
(82,12,'Green Tea',NULL,100.00,1),
(83,12,'Lemon Tea',NULL,90.00,1),
(84,12,'Black Tea',NULL,70.00,1),
(85,12,'Coffee',NULL,120.00,1),
(86,12,'Fresh Lemonade',NULL,150.00,1),
(87,12,'Veg Momo',NULL,150.00,1),
(88,12,'Paneer Momo',NULL,220.00,1),
(89,12,'Cheese Fries',NULL,180.00,1),
(90,12,'Red Velvet Cake',NULL,250.00,1),
(91,12,'Brownie',NULL,200.00,1),
(92,12,'Ice Cream',NULL,150.00,1);
/*!40000 ALTER TABLE `menu_items` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `reservations`
--

DROP TABLE IF EXISTS `reservations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reservations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cafe_id` int(11) NOT NULL,
  `customer_name` varchar(100) NOT NULL,
  `email` varchar(100) NOT NULL,
  `phone` varchar(20) NOT NULL,
  `reservation_date` date NOT NULL,
  `reservation_time` varchar(20) NOT NULL,
  `people` int(11) NOT NULL,
  `message` text DEFAULT NULL,
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  PRIMARY KEY (`id`),
  KEY `cafe_id` (`cafe_id`),
  CONSTRAINT `reservations_ibfk_1` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reservations`
--

LOCK TABLES `reservations` WRITE;
/*!40000 ALTER TABLE `reservations` DISABLE KEYS */;
set autocommit=0;
/*!40000 ALTER TABLE `reservations` ENABLE KEYS */;
UNLOCK TABLES;
commit;

--
-- Table structure for table `reviews`
--

DROP TABLE IF EXISTS `reviews`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `reviews` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `cafe_id` int(11) NOT NULL,
  `user_name` varchar(100) NOT NULL,
  `comment` text NOT NULL,
  `rating` int(11) NOT NULL CHECK (`rating` between 1 and 5),
  `created_at` timestamp NULL DEFAULT current_timestamp(),
  `image_path` varchar(255) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `fk_reviews_cafe` (`cafe_id`),
  CONSTRAINT `fk_reviews_cafe` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE,
  CONSTRAINT `reviews_ibfk_1` FOREIGN KEY (`cafe_id`) REFERENCES `cafes` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_uca1400_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reviews`
--

LOCK TABLES `reviews` WRITE;
/*!40000 ALTER TABLE `reviews` DISABLE KEYS */;
set autocommit=0;
INSERT INTO `reviews` VALUES
(4,12,'Ram Sharma','good\r\n',4,'2026-08-01 17:36:31',NULL),
(6,12,'saurav Bista','Best Cafee ever',5,'2026-08-02 16:08:32','uploads/chintan_chautari_2.jpeg');
/*!40000 ALTER TABLE `reviews` ENABLE KEYS */;
UNLOCK TABLES;
commit;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*M!100616 SET NOTE_VERBOSITY=@OLD_NOTE_VERBOSITY */;

-- Dump completed on 2026-08-05  8:10:42
