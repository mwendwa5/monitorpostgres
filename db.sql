CREATE TABLE servers (
  id INTEGER PRIMARY KEY,
  sname char(30) NOT NULL,
  endpoint varchar(150) ,
  active bool DEFAULT '1',
  confail INTEGER DEFAULT '0',
  CONSTRAINT sname_unique UNIQUE (sname),
  CONSTRAINT endpt_unique UNIQUE (endpoint)
);

CREATE TABLE uptimealert (
  uptimeAlertID INTEGER PRIMARY KEY,
  host varchar(200) NOT NULL,
  status varchar(20) NOT NULL DEFAULT 'offline',
  alertDate timestamp NOT NULL DEFAULT now(),
  CONSTRAINT host_unique UNIQUE(host),
  CONSTRAINT alert_unique UNIQUE (alertDate)
);
