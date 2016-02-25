
top_srcdir=`pwd`/..

DOMAIN=update-manager
PO_FILES := $(wildcard *.po)
CONTACT=sebastian.heinlein@web.de
XGETTEXT_ARGS = --msgid-bugs-address=$(CONTACT)
XGETTEXT_ARGS += --keyword=unicode_gettext:2 --keyword=unicode_ngettext:2,3
XGETTEXT_ARGS += --language=python

all: update-po

# update the pot
$(DOMAIN).pot:
	XGETTEXT_ARGS="$(XGETTEXT_ARGS)" intltool-update -p -g $(DOMAIN)

# merge the new stuff into the po files
merge-po: $(PO_FILES)
	XGETTEXT_ARGS="$(XGETTEXT_ARGS)" intltool-update -r -g $(DOMAIN); 

# create mo from the pos
%.mo : %.po
	mkdir -p mo/$(subst .po,,$<)/LC_MESSAGES/ 
	msgfmt $< -o mo/$(subst .po,,$<)/LC_MESSAGES/$(DOMAIN).mo 

# dummy target 
update-po: $(DOMAIN).pot merge-po $(patsubst %.po,%.mo,$(wildcard *.po))

