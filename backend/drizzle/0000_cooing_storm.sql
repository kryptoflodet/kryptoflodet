CREATE TABLE `articles` (
	`id` text PRIMARY KEY NOT NULL,
	`event_key` text NOT NULL,
	`source_id` text,
	`published_at` text NOT NULL,
	`imported_at` text NOT NULL,
	`category` text NOT NULL,
	`status` text NOT NULL,
	`importance` integer DEFAULT 1 NOT NULL,
	`visible` integer DEFAULT true NOT NULL,
	`payload_json` text NOT NULL,
	FOREIGN KEY (`source_id`) REFERENCES `sources`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE INDEX `articles_published` ON `articles` (`published_at`);--> statement-breakpoint
CREATE INDEX `articles_event` ON `articles` (`event_key`);--> statement-breakpoint
CREATE INDEX `articles_filter` ON `articles` (`visible`,`status`,`category`);--> statement-breakpoint
CREATE TABLE `evidence` (
	`id` text PRIMARY KEY NOT NULL,
	`article_id` text,
	`source_id` text,
	`origin_id` text NOT NULL,
	`url` text NOT NULL,
	`direct` integer DEFAULT false NOT NULL,
	`verified` integer DEFAULT false NOT NULL,
	FOREIGN KEY (`article_id`) REFERENCES `articles`(`id`) ON UPDATE no action ON DELETE no action,
	FOREIGN KEY (`source_id`) REFERENCES `sources`(`id`) ON UPDATE no action ON DELETE no action
);
--> statement-breakpoint
CREATE TABLE `ingestion_runs` (
	`id` text PRIMARY KEY NOT NULL,
	`connector` text NOT NULL,
	`started_at` text NOT NULL,
	`finished_at` text,
	`status` text NOT NULL,
	`imported` integer DEFAULT 0 NOT NULL,
	`error` text
);
--> statement-breakpoint
CREATE TABLE `sources` (
	`id` text PRIMARY KEY NOT NULL,
	`name` text NOT NULL,
	`type` text NOT NULL,
	`channel` text NOT NULL,
	`url` text NOT NULL,
	`trust` integer DEFAULT 0 NOT NULL,
	`enabled` integer DEFAULT false NOT NULL,
	`independence_group` text NOT NULL,
	`config_json` text DEFAULT '{}' NOT NULL
);
