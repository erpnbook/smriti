/*M!999999\- enable the sandbox mode */ 
-- MariaDB dump 10.19  Distrib 10.11.14-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: db    Database: _627132d433fb72c2
-- ------------------------------------------------------
-- Server version	11.8.8-MariaDB-ubu2404

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `tabSMRITI Company Settings`
--

DROP TABLE IF EXISTS `tabSMRITI Company Settings`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Company Settings` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `company` varchar(140) DEFAULT NULL,
  `store_trade_name` varchar(140) DEFAULT NULL,
  `store_logo_url` varchar(140) DEFAULT NULL,
  `brand_color` varchar(140) DEFAULT '#1a73e8',
  `receipt_footer_text` text DEFAULT 'Thank you for shopping with us!',
  `invoice_series_prefix` varchar(140) DEFAULT 'SINV-',
  `default_warehouse` varchar(140) DEFAULT NULL,
  `default_pos_profile` varchar(140) DEFAULT NULL,
  `default_walk_in_customer` varchar(140) DEFAULT NULL,
  `default_intrastate_tax_template` varchar(140) DEFAULT NULL,
  `default_interstate_tax_template` varchar(140) DEFAULT NULL,
  `loyalty_enabled` tinyint(4) NOT NULL DEFAULT 0,
  `loyalty_points_per_rupee` decimal(21,9) NOT NULL DEFAULT 1.000000000,
  `cloud_backup_enabled` tinyint(4) NOT NULL DEFAULT 0,
  `cloud_provider` varchar(140) DEFAULT NULL,
  `s3_bucket` varchar(140) DEFAULT NULL,
  `s3_access_key` varchar(140) DEFAULT NULL,
  `s3_secret_key` text DEFAULT NULL,
  `s3_region` varchar(140) DEFAULT 'ap-south-1',
  `size_groups_json` longtext DEFAULT NULL,
  `destinationwise_taxes_json` longtext DEFAULT NULL,
  `backup_settings_json` longtext DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  `custom_business_type` varchar(140) DEFAULT 'Footwear',
  `custom_print_profiles_json` longtext DEFAULT NULL,
  `default_printer_ip` varchar(140) DEFAULT NULL,
  `default_printer_port` int(11) NOT NULL DEFAULT 9100,
  `default_printer_lang` varchar(140) DEFAULT 'ZPL',
  `default_label_size` varchar(140) DEFAULT '50x25',
  PRIMARY KEY (`name`),
  UNIQUE KEY `company` (`company`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Report Role`
--

DROP TABLE IF EXISTS `tabSMRITI Report Role`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Report Role` (
  `name` bigint(20) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `role` varchar(140) DEFAULT NULL,
  `parent` varchar(140) DEFAULT NULL,
  `parentfield` varchar(140) DEFAULT NULL,
  `parenttype` varchar(140) DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `parent` (`parent`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Report Template`
--

DROP TABLE IF EXISTS `tabSMRITI Report Template`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Report Template` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `report_key` varchar(140) DEFAULT NULL,
  `report_name` varchar(140) DEFAULT NULL,
  `report_category` varchar(140) DEFAULT NULL,
  `source_doctype` varchar(140) DEFAULT NULL,
  `columns_json` longtext DEFAULT NULL,
  `filters_json` longtext DEFAULT NULL,
  `group_by` varchar(140) DEFAULT NULL,
  `order_by` varchar(140) DEFAULT NULL,
  `branch_restricted` tinyint(4) NOT NULL DEFAULT 0,
  `company_restricted` tinyint(4) NOT NULL DEFAULT 0,
  `cache_minutes` int(11) NOT NULL DEFAULT 0,
  `schema_version` int(11) NOT NULL DEFAULT 1,
  `layout_json` longtext DEFAULT NULL,
  `chart_json` longtext DEFAULT NULL,
  `pivot_json` longtext DEFAULT NULL,
  `widget_json` longtext DEFAULT NULL,
  `is_public` tinyint(4) NOT NULL DEFAULT 1,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `report_key` (`report_key`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Saved View`
--

DROP TABLE IF EXISTS `tabSMRITI Saved View`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Saved View` (
  `name` bigint(20) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `view_name` varchar(140) DEFAULT NULL,
  `report_template` varchar(140) DEFAULT NULL,
  `user` varchar(140) DEFAULT NULL,
  `applied_filters_json` longtext DEFAULT NULL,
  `visible_columns_json` longtext DEFAULT NULL,
  `is_default` tinyint(4) NOT NULL DEFAULT 0,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Address Audit Log`
--

DROP TABLE IF EXISTS `tabSMRITI Address Audit Log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Address Audit Log` (
  `name` bigint(20) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `changed_by` varchar(140) DEFAULT NULL,
  `changed_at` datetime(6) DEFAULT NULL,
  `field_name` varchar(140) DEFAULT NULL,
  `old_value` text DEFAULT NULL,
  `new_value` text DEFAULT NULL,
  `company` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Key Custodian`
--

DROP TABLE IF EXISTS `tabSMRITI Key Custodian`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Key Custodian` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `custodian_name` varchar(140) DEFAULT NULL,
  `email` varchar(140) DEFAULT NULL,
  `verified` tinyint(4) NOT NULL DEFAULT 0,
  `verification_date` datetime(6) DEFAULT NULL,
  `last_recovery_sent` datetime(6) DEFAULT NULL,
  `status` varchar(140) DEFAULT 'Pending',
  `otp_hash` varchar(140) DEFAULT NULL,
  `otp_expiry` datetime(6) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `email` (`email`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Print Job`
--

DROP TABLE IF EXISTS `tabSMRITI Print Job`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Print Job` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `job_id` varchar(140) DEFAULT NULL,
  `printer_ip` varchar(140) DEFAULT NULL,
  `printer_port` int(11) NOT NULL DEFAULT 9100,
  `status` varchar(140) DEFAULT 'Queued',
  `completed_on` datetime(6) DEFAULT NULL,
  `payload_hash` varchar(140) DEFAULT NULL,
  `payload_preview` varchar(140) DEFAULT NULL,
  `template_name` varchar(140) DEFAULT NULL,
  `labels_count` int(11) NOT NULL DEFAULT 0,
  `requested_by` varchar(140) DEFAULT NULL,
  `request_ip` varchar(140) DEFAULT NULL,
  `request_user_agent` text DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  `item_code` varchar(140) DEFAULT NULL,
  `barcode` varchar(140) DEFAULT NULL,
  `print_qty` int(11) NOT NULL DEFAULT 0,
  `error_message` text DEFAULT NULL,
  `created_by` varchar(140) DEFAULT NULL,
  `created_on` datetime(6) DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `job_id` (`job_id`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Heel Type`
--

DROP TABLE IF EXISTS `tabSMRITI Heel Type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Heel Type` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Outsole`
--

DROP TABLE IF EXISTS `tabSMRITI Outsole`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Outsole` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Upper Material`
--

DROP TABLE IF EXISTS `tabSMRITI Upper Material`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Upper Material` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Gender`
--

DROP TABLE IF EXISTS `tabSMRITI Gender`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Gender` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Purchase Class`
--

DROP TABLE IF EXISTS `tabSMRITI Purchase Class`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Purchase Class` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Merchandise Category`
--

DROP TABLE IF EXISTS `tabSMRITI Merchandise Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Merchandise Category` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `tabSMRITI Sub Category`
--

DROP TABLE IF EXISTS `tabSMRITI Sub Category`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8mb4 */;
CREATE TABLE `tabSMRITI Sub Category` (
  `name` varchar(140) NOT NULL,
  `creation` datetime(6) DEFAULT NULL,
  `modified` datetime(6) DEFAULT NULL,
  `modified_by` varchar(140) DEFAULT NULL,
  `owner` varchar(140) DEFAULT NULL,
  `docstatus` tinyint(4) NOT NULL DEFAULT 0,
  `idx` int(11) NOT NULL DEFAULT 0,
  `attribute_value` varchar(140) DEFAULT NULL,
  `_user_tags` text DEFAULT NULL,
  `_comments` text DEFAULT NULL,
  `_assign` text DEFAULT NULL,
  `_liked_by` text DEFAULT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `attribute_value` (`attribute_value`),
  KEY `creation` (`creation`),
  KEY `modified` (`modified`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci ROW_FORMAT=DYNAMIC;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-06-18 11:24:11
