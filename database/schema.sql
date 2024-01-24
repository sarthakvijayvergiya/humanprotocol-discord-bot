CREATE TABLE IF NOT EXISTS `user_settings` (
  `user_id` VARCHAR(20) NOT NULL,
  `result_channel_id` VARCHAR(20),
  PRIMARY KEY (`user_id`)
);