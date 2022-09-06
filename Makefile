# parolottero-languages
# Copyright (C) 2021-2022 Salvo "LtWorf" Tomaselli
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# author Salvo "LtWorf" Tomaselli <tiposchi@tiscali.it>

.PHONY: wordlists
wordlists: language_data/swedish language_data/english language_data/american language_data/italian language_data/sicilian
#TODO language_data/greek
#TODO language_data/basque
#TODO language_data/french

language_data/%: dict/sicilian dict/italian dict/swedish.xpi dict/english.xpi dict/american.xpi dict/greek.xpi dict/basque.xpi dict/french.xpi
	mkdir -p language_data
	utils/lang_init.py `basename $@` $@ $@.wordlist

.PHONY: clean
clean:
	$(RM) -r language_data
	$(RM) -r dict

.PHONY: install
install: wordlists
	install -d $${DESTDIR:-/}/usr/share/games/parolottero/language_data
	cp language_data/* $${DESTDIR:-/}/usr/share/games/parolottero/language_data/

.PHONY: dist
dist: wordlists
	rm -rf /tmp/parolottero-languages/
	rm -rf /tmp/parolottero-languages-*
	mkdir /tmp/parolottero-languages/
	cp -R * /tmp/parolottero-languages/
	( \
		cd /tmp; \
		tar --exclude '*.user' -zcf parolottero-languages.tar.gz \
			parolottero-languages/dict \
			parolottero-languages/extralist \
			parolottero-languages/utils \
			parolottero-languages/Makefile \
			parolottero-languages/LICENSE \
			parolottero-languages/README.md \
			parolottero-languages/CHANGELOG \
			parolottero-languages/CODE_OF_CONDUCT.md \
	)
	mv /tmp/parolottero-languages.tar.gz ./parolottero-languages_`head -1 CHANGELOG`.orig.tar.gz
	gpg --sign --armor --detach-sign ./parolottero-languages_`head -1 CHANGELOG`.orig.tar.gz

.PHONY: deb-pkg
deb-pkg: dist wordlists
	mkdir -p deb-pkg
	cp language_data/* deb-pkg
	./compress_lang.sh
	$(RM) -r /tmp/parolottero*
	mv parolottero-languages*orig* /tmp
	cd /tmp; tar -xf parolottero-languages*orig*.gz
	cp -r debian /tmp/parolottero-languages/
	cd /tmp/parolottero-languages; dpkg-buildpackage --changes-option=-S
	mv /tmp/parolottero*.* deb-pkg
	lintian --pedantic -E --color auto -i -I deb-pkg/*changes deb-pkg/*deb

dict/swedish.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/3539390/gorans_hemmasnickrade_ordli-1.21.xpi -O $@
	touch $@
dict/english.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/3956029/british_english_dictionary_2-3.0.9.xpi -O $@
	touch $@
dict/american.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/3893473/us_english_dictionary-91.0.xpi -O $@
	touch $@
dict/greek.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/1163899/greek_spellchecking_dictionary-0.8.5.2webext.xpi -O $@
	touch $@
dict/italian:
	mkdir -p dict
	wget https://github.com/napolux/paroleitaliane/raw/master/paroleitaliane/280000_parole_italiane.txt -O $@
	# https://addons.mozilla.org/firefox/downloads/file/3693497/dizionario_italiano-5.1.xpi -O $@
	touch $@
dict/basque.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/1163937/xuxen-5.1.0.1webext.xpi -O $@
	touch $@
dict/french.xpi:
	mkdir -p dict
	wget https://addons.mozilla.org/firefox/downloads/file/3581786/dictionnaire_francais1-7.0b.xpi -O $@
	touch $@
dict/sicilian:
	mkdir -p dict
	wget https://github.com/ltworf/sicilianu/releases/download/2022-03-18/wsicilian-2022-03-18.tar.gz -O $@.tar.gz
	cd dict; tar -xf `basename $@.tar.gz`
	rm $@.tar.gz
	mv dict/wsicilian $@
	touch $@
