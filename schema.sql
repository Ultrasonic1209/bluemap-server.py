-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: 172.17.0.7
-- Generation Time: Aug 06, 2022 at 11:24 AM
-- Server version: 10.8.3-MariaDB-1:10.8.3+maria~jammy
-- PHP Version: 8.0.22

-- used for reference in constructing `models.py`

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

--
-- Database: `bluemap`
--

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_map`
--

CREATE TABLE `bluemap_map` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `map_id` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_map_meta`
--

CREATE TABLE `bluemap_map_meta` (
  `map` smallint(5) UNSIGNED NOT NULL,
  `key` varchar(255) NOT NULL,
  `value` longblob NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_map_tile`
--

CREATE TABLE `bluemap_map_tile` (
  `map` smallint(5) UNSIGNED NOT NULL,
  `type` smallint(5) UNSIGNED NOT NULL,
  `x` int(11) NOT NULL,
  `z` int(11) NOT NULL,
  `compression` smallint(5) UNSIGNED NOT NULL,
  `changed` timestamp NOT NULL DEFAULT current_timestamp() ON UPDATE current_timestamp(),
  `data` longblob NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_map_tile_compression`
--

CREATE TABLE `bluemap_map_tile_compression` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `compression` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_map_tile_type`
--

CREATE TABLE `bluemap_map_tile_type` (
  `id` smallint(5) UNSIGNED NOT NULL,
  `type` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `bluemap_storage_meta`
--

CREATE TABLE `bluemap_storage_meta` (
  `key` varchar(255) NOT NULL,
  `value` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Indexes for dumped tables
--

--
-- Indexes for table `bluemap_map`
--
ALTER TABLE `bluemap_map`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `map_id` (`map_id`);

--
-- Indexes for table `bluemap_map_meta`
--
ALTER TABLE `bluemap_map_meta`
  ADD PRIMARY KEY (`map`,`key`);

--
-- Indexes for table `bluemap_map_tile`
--
ALTER TABLE `bluemap_map_tile`
  ADD PRIMARY KEY (`map`,`type`,`x`,`z`),
  ADD KEY `fk_bluemap_map_tile_type` (`type`),
  ADD KEY `fk_bluemap_map_tile_compression` (`compression`);

--
-- Indexes for table `bluemap_map_tile_compression`
--
ALTER TABLE `bluemap_map_tile_compression`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `compression` (`compression`);

--
-- Indexes for table `bluemap_map_tile_type`
--
ALTER TABLE `bluemap_map_tile_type`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `type` (`type`);

--
-- Indexes for table `bluemap_storage_meta`
--
ALTER TABLE `bluemap_storage_meta`
  ADD PRIMARY KEY (`key`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `bluemap_map`
--
ALTER TABLE `bluemap_map`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bluemap_map_tile_compression`
--
ALTER TABLE `bluemap_map_tile_compression`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `bluemap_map_tile_type`
--
ALTER TABLE `bluemap_map_tile_type`
  MODIFY `id` smallint(5) UNSIGNED NOT NULL AUTO_INCREMENT;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `bluemap_map_meta`
--
ALTER TABLE `bluemap_map_meta`
  ADD CONSTRAINT `fk_bluemap_map_meta_map` FOREIGN KEY (`map`) REFERENCES `bluemap_map` (`id`);

--
-- Constraints for table `bluemap_map_tile`
--
ALTER TABLE `bluemap_map_tile`
  ADD CONSTRAINT `fk_bluemap_map_tile_compression` FOREIGN KEY (`compression`) REFERENCES `bluemap_map_tile_compression` (`id`),
  ADD CONSTRAINT `fk_bluemap_map_tile_map` FOREIGN KEY (`map`) REFERENCES `bluemap_map` (`id`),
  ADD CONSTRAINT `fk_bluemap_map_tile_type` FOREIGN KEY (`type`) REFERENCES `bluemap_map_tile_type` (`id`);
COMMIT;
