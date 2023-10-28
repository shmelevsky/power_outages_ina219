CREATE TABLE outages (date int, event BOOLEAN, sent BOOLEAN default false);
CREATE INDEX index_date ON outages(date);