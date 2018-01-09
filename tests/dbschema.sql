
CREATE TABLE domainelement_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE languageidentifier_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	language_pk INTEGER NOT NULL, 
	identifier_pk INTEGER NOT NULL, 
	description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitparameter_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE sentence_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitdomainelement_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	unitparameter_pk INTEGER NOT NULL, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE parameter (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (name), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	glottolog_id VARCHAR, 
	google_book_search_id VARCHAR, 
	bibtex_type VARCHAR(13), 
	author VARCHAR, 
	year VARCHAR, 
	title VARCHAR, 
	type VARCHAR, 
	booktitle VARCHAR, 
	editor VARCHAR, 
	pages VARCHAR, 
	edition VARCHAR, 
	journal VARCHAR, 
	school VARCHAR, 
	address VARCHAR, 
	url VARCHAR, 
	note VARCHAR, 
	number VARCHAR, 
	series VARCHAR, 
	volume VARCHAR, 
	publisher VARCHAR, 
	organization VARCHAR, 
	chapter VARCHAR, 
	howpublished VARCHAR, 
	year_int INTEGER, 
	startpage_int INTEGER, 
	pages_int INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CONSTRAINT ck_entry_type CHECK (bibtex_type IN ('conference', 'manual', 'techreport', 'phdthesis', 'inproceedings', 'booklet', 'unpublished', 'misc', 'inbook', 'proceedings', 'book', 'incollection', 'mastersthesis', 'article')), 
	CHECK (active IN (0, 1))
)


CREATE TABLE parameter_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE dataset_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE identifier (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	id VARCHAR, 
	type VARCHAR, 
	lang VARCHAR(3), 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (name, type, description, lang), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitvalue_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	unit_pk INTEGER NOT NULL, 
	unitparameter_pk INTEGER NOT NULL, 
	contribution_pk INTEGER, 
	unitdomainelement_pk INTEGER, 
	frequency FLOAT, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitdomainelement_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contribution_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE sentencereference_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	sentence_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE sentence_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	analyzed VARCHAR, 
	gloss VARCHAR, 
	type VARCHAR, 
	source VARCHAR, 
	comment VARCHAR, 
	original_script VARCHAR, 
	xhtml VARCHAR, 
	markup_text VARCHAR, 
	markup_analyzed VARCHAR, 
	markup_gloss VARCHAR, 
	markup_comment VARCHAR, 
	language_pk INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE valueset_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE valueset_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE value_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contribution (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	date DATE, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (name), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitvalue_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitparameter (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE dataset (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	published DATE, 
	publisher_name VARCHAR, 
	publisher_place VARCHAR, 
	publisher_url VARCHAR, 
	license VARCHAR, 
	domain VARCHAR NOT NULL, 
	contact VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributor (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	url VARCHAR, 
	email VARCHAR, 
	address VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (name), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unit_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE identifier_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	id VARCHAR, 
	type VARCHAR, 
	lang VARCHAR(3), 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitdomainelement_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE valuesetreference_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	valueset_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE glossabbreviation_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitparameter_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributor_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE domainelement_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	parameter_pk INTEGER NOT NULL, 
	number INTEGER, 
	abbr VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	latitude FLOAT CHECK (-90 <= latitude and latitude <= 90), 
	longitude FLOAT CHECK (-180 <= longitude and longitude <= 180 ), 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1))
)


CREATE TABLE value_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE value_history (
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	pk INTEGER NOT NULL, 
	valueset_pk INTEGER NOT NULL, 
	domainelement_pk INTEGER, 
	frequency FLOAT, 
	confidence VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unit_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE dataset_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE editor_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	dataset_pk INTEGER NOT NULL, 
	contributor_pk INTEGER NOT NULL, 
	ord INTEGER, 
	"primary" BOOLEAN, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK ("primary" IN (0, 1)), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	glottolog_id VARCHAR, 
	google_book_search_id VARCHAR, 
	bibtex_type VARCHAR(13), 
	author VARCHAR, 
	year VARCHAR, 
	title VARCHAR, 
	type VARCHAR, 
	booktitle VARCHAR, 
	editor VARCHAR, 
	pages VARCHAR, 
	edition VARCHAR, 
	journal VARCHAR, 
	school VARCHAR, 
	address VARCHAR, 
	url VARCHAR, 
	note VARCHAR, 
	number VARCHAR, 
	series VARCHAR, 
	volume VARCHAR, 
	publisher VARCHAR, 
	organization VARCHAR, 
	chapter VARCHAR, 
	howpublished VARCHAR, 
	year_int INTEGER, 
	startpage_int INTEGER, 
	pages_int INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CONSTRAINT ck_entry_type CHECK (bibtex_type IN ('conference', 'manual', 'techreport', 'phdthesis', 'inproceedings', 'booklet', 'unpublished', 'misc', 'inbook', 'proceedings', 'book', 'incollection', 'mastersthesis', 'article')), 
	CHECK (active IN (0, 1))
)


CREATE TABLE parameter_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE sentence_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributor_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	url VARCHAR, 
	email VARCHAR, 
	address VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE languagesource_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	language_pk INTEGER NOT NULL, 
	source_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE valuesentence_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	value_pk INTEGER NOT NULL, 
	sentence_pk INTEGER NOT NULL, 
	description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contribution_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contribution_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	date DATE, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	latitude FLOAT CHECK (-90 <= latitude and latitude <= 90), 
	longitude FLOAT CHECK (-180 <= longitude and longitude <= 180 ), 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributor_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE domainelement_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unit_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE dataset_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	published DATE, 
	publisher_name VARCHAR, 
	publisher_place VARCHAR, 
	publisher_url VARCHAR, 
	license VARCHAR, 
	domain VARCHAR NOT NULL, 
	contact VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE config (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributionreference_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	contribution_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE parameter_data_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributioncontributor_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	contribution_pk INTEGER NOT NULL, 
	contributor_pk INTEGER NOT NULL, 
	ord INTEGER, 
	"primary" BOOLEAN, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK ("primary" IN (0, 1)), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitvalue_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE valueset_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER NOT NULL, 
	parameter_pk INTEGER NOT NULL, 
	contribution_pk INTEGER, 
	source VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitparameter_files_history (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES language (pk)
)


CREATE TABLE customlanguage (
	pk INTEGER NOT NULL, 
	custom VARCHAR, 
	PRIMARY KEY (pk), 
	FOREIGN KEY(pk) REFERENCES language (pk)
)


CREATE TABLE sentence (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	analyzed VARCHAR, 
	gloss VARCHAR, 
	type VARCHAR, 
	source VARCHAR, 
	comment VARCHAR, 
	original_script VARCHAR, 
	xhtml VARCHAR, 
	markup_text VARCHAR, 
	markup_analyzed VARCHAR, 
	markup_gloss VARCHAR, 
	markup_comment VARCHAR, 
	language_pk INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE language_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES language (pk)
)


CREATE TABLE languagesource (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	language_pk INTEGER NOT NULL, 
	source_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (language_pk, source_pk), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	FOREIGN KEY(source_pk) REFERENCES source (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contribution_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES contribution (pk)
)


CREATE TABLE unitdomainelement (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	unitparameter_pk INTEGER NOT NULL, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (unitparameter_pk, name), 
	UNIQUE (unitparameter_pk, ord), 
	UNIQUE (id), 
	FOREIGN KEY(unitparameter_pk) REFERENCES unitparameter (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES source (pk)
)


CREATE TABLE parameter_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES parameter (pk)
)


CREATE TABLE dataset_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES dataset (pk)
)


CREATE TABLE unitparameter_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitparameter (pk)
)


CREATE TABLE valueset (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER NOT NULL, 
	parameter_pk INTEGER NOT NULL, 
	contribution_pk INTEGER, 
	source VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (language_pk, parameter_pk, contribution_pk), 
	UNIQUE (id), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	FOREIGN KEY(parameter_pk) REFERENCES parameter (pk), 
	FOREIGN KEY(contribution_pk) REFERENCES contribution (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributor_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES contributor (pk)
)


CREATE TABLE contribution_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES contribution (pk)
)


CREATE TABLE glossabbreviation (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id, language_pk), 
	UNIQUE (id), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE contributioncontributor (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	contribution_pk INTEGER NOT NULL, 
	contributor_pk INTEGER NOT NULL, 
	ord INTEGER, 
	"primary" BOOLEAN, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (contribution_pk, contributor_pk), 
	FOREIGN KEY(contribution_pk) REFERENCES contribution (pk), 
	FOREIGN KEY(contributor_pk) REFERENCES contributor (pk), 
	CHECK ("primary" IN (0, 1)), 
	CHECK (active IN (0, 1))
)


CREATE TABLE customlanguage_history (
	pk INTEGER NOT NULL, 
	custom VARCHAR, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk, version), 
	FOREIGN KEY(pk, version) REFERENCES language_history (pk, version)
)


CREATE TABLE dataset_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES dataset (pk)
)


CREATE TABLE unit (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	language_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (language_pk, id), 
	UNIQUE (id), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE languageidentifier (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	language_pk INTEGER NOT NULL, 
	identifier_pk INTEGER NOT NULL, 
	description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (language_pk, identifier_pk), 
	FOREIGN KEY(language_pk) REFERENCES language (pk), 
	FOREIGN KEY(identifier_pk) REFERENCES identifier (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE editor (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	dataset_pk INTEGER NOT NULL, 
	contributor_pk INTEGER NOT NULL, 
	ord INTEGER, 
	"primary" BOOLEAN, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (dataset_pk, contributor_pk), 
	FOREIGN KEY(dataset_pk) REFERENCES dataset (pk), 
	FOREIGN KEY(contributor_pk) REFERENCES contributor (pk), 
	CHECK ("primary" IN (0, 1)), 
	CHECK (active IN (0, 1))
)


CREATE TABLE source_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES source (pk)
)


CREATE TABLE domainelement (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	parameter_pk INTEGER NOT NULL, 
	number INTEGER, 
	abbr VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (parameter_pk, name), 
	UNIQUE (parameter_pk, number), 
	UNIQUE (id), 
	FOREIGN KEY(parameter_pk) REFERENCES parameter (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitparameter_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitparameter (pk)
)


CREATE TABLE parameter_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES parameter (pk)
)


CREATE TABLE contributionreference (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	contribution_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (contribution_pk, source_pk, description), 
	FOREIGN KEY(contribution_pk) REFERENCES contribution (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(source_pk) REFERENCES source (pk)
)


CREATE TABLE contributor_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES contributor (pk)
)


CREATE TABLE valueset_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES valueset (pk)
)


CREATE TABLE unitdomainelement_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitdomainelement (pk)
)


CREATE TABLE sentence_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES sentence (pk)
)


CREATE TABLE sentencereference (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	sentence_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (sentence_pk, source_pk, description), 
	FOREIGN KEY(sentence_pk) REFERENCES sentence (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(source_pk) REFERENCES source (pk)
)


CREATE TABLE unitvalue (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	unit_pk INTEGER NOT NULL, 
	unitparameter_pk INTEGER NOT NULL, 
	contribution_pk INTEGER, 
	unitdomainelement_pk INTEGER, 
	frequency FLOAT, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (unit_pk, unitparameter_pk, contribution_pk, name, unitdomainelement_pk), 
	UNIQUE (id), 
	FOREIGN KEY(unit_pk) REFERENCES unit (pk), 
	FOREIGN KEY(unitparameter_pk) REFERENCES unitparameter (pk), 
	FOREIGN KEY(contribution_pk) REFERENCES contribution (pk), 
	FOREIGN KEY(unitdomainelement_pk) REFERENCES unitdomainelement (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE sentence_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES sentence (pk)
)


CREATE TABLE unit_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unit (pk)
)


CREATE TABLE unitdomainelement_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitdomainelement (pk)
)


CREATE TABLE domainelement_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES domainelement (pk)
)


CREATE TABLE valuesetreference (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	description VARCHAR, 
	valueset_pk INTEGER NOT NULL, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	source_pk INTEGER NOT NULL, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (valueset_pk, source_pk, description), 
	FOREIGN KEY(valueset_pk) REFERENCES valueset (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(source_pk) REFERENCES source (pk)
)


CREATE TABLE unit_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unit (pk)
)


CREATE TABLE value (
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	pk INTEGER NOT NULL, 
	valueset_pk INTEGER NOT NULL, 
	domainelement_pk INTEGER, 
	frequency FLOAT, 
	confidence VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (valueset_pk, name, domainelement_pk), 
	UNIQUE (id), 
	FOREIGN KEY(valueset_pk) REFERENCES valueset (pk), 
	FOREIGN KEY(domainelement_pk) REFERENCES domainelement (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE domainelement_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES domainelement (pk)
)


CREATE TABLE valueset_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES valueset (pk)
)


CREATE TABLE value_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES value (pk)
)


CREATE TABLE valuesentence (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	polymorphic_type VARCHAR(20), 
	value_pk INTEGER NOT NULL, 
	sentence_pk INTEGER NOT NULL, 
	description VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (value_pk, sentence_pk), 
	FOREIGN KEY(value_pk) REFERENCES value (pk), 
	FOREIGN KEY(sentence_pk) REFERENCES sentence (pk), 
	CHECK (active IN (0, 1))
)


CREATE TABLE unitvalue_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitvalue (pk)
)


CREATE TABLE unitvalue_data (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	"key" VARCHAR, 
	value VARCHAR, 
	ord INTEGER, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES unitvalue (pk)
)


CREATE TABLE value_files (
	pk INTEGER NOT NULL, 
	jsondata VARCHAR, 
	id VARCHAR, 
	name VARCHAR, 
	description VARCHAR, 
	markup_description VARCHAR, 
	ord INTEGER, 
	mime_type VARCHAR, 
	updated DATETIME, 
	active BOOLEAN, 
	created DATETIME, 
	object_pk INTEGER, 
	version INTEGER NOT NULL, 
	PRIMARY KEY (pk), 
	UNIQUE (id), 
	CHECK (active IN (0, 1)), 
	FOREIGN KEY(object_pk) REFERENCES value (pk)
)

