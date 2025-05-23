#!/bin/sh

# script to add apt.postgresql.org to sources.list.d

# Copyright (C) 2013-2023 Christoph Berg <myon@debian.org>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# The full text of the GPL is distributed as in
# /usr/share/common-licenses/GPL-2 on Debian systems.

SOURCESLIST="/etc/apt/sources.list.d/pgdg.sources"
TYPES="deb"
COMPONENTS="main"
PGDG="pgdg"

# variables imported from https://git.postgresql.org/gitweb/?p=pgapt.git;a=blob;f=pgapt.conf
# checked out in $HOME/apt.postgresql.org/; run "make" to update
PG_BETA_VERSION=""
PG_DEVEL_VERSION="18"
PG_REPOSITORY_DISTS="sid trixie bookworm bullseye oracular noble jammy focal"
PG_ARCHIVE_DISTS="sid trixie bookworm bullseye buster stretch jessie wheezy squeeze lenny etch oracular noble mantic lunar kinetic jammy impish hirsute groovy focal eoan disco cosmic bionic zesty xenial wily utopic saucy precise lucid"

while getopts "c:f:h:ipstv:y" opt ; do
    case $opt in
        c) COMPONENTS="main $OPTARG" ;; # make these extra components available
        f) SOURCESLIST=$OPTARG ;; # sources.list filename to write to
        h) HOST="$OPTARG" ;; # hostname to use in sources.list
        i) INSTALL="yes" ;; # install packages for version given with -v
        p) PURGE="yes" ;; # purge existing postgresql packages
        s) TYPES="deb deb-src" ;; # include source repository as well
        t) PGDG="pgdg-testing" ;; # use *-pgdg or *-pgdg-testing
        v) PGVERSION="$OPTARG" ;; # set up sources.list to use this version (useful for beta/devel packages)
        y) ;; # don't ask for confirmation
        *) exit 5 ;;
    esac
    YES="yes" # don't ask for confirmation if any option is given
done
# shift away args
shift $((OPTIND - 1))
# check options
if [ "$INSTALL" ] && [ -z "$PGVERSION" ]; then
    echo "With -i, a version to install must be provided (-v)"
    exit 1
fi

# codename from command line
CODENAME="$1"
# parse os-release
if [ -z "$CODENAME" ] && [ -f /etc/os-release ]; then
    . /etc/os-release
    if [ "$VERSION_CODENAME" ]; then # added in buster/xenial
        CODENAME="$VERSION_CODENAME"
    else
        # Debian: VERSION="7.0 (wheezy)"
        # Ubuntu: VERSION="13.04, Raring Ringtail"
        #         VERSION="18.04.1 LTS (Bionic Beaver)"
        CODENAME=$(echo $VERSION | sed -ne 's/.*(\(.*\)).*/\1/') # works on Debian only
    fi
fi
# try lsb_release
if [ -z "$CODENAME" ] && command -v lsb_release >/dev/null; then
    CODENAME=$(lsb_release -cs 2>/dev/null)
fi
# guess from sources.list
if [ -z "$CODENAME" ] && [ -f /etc/apt/sources.list ]; then
    CODENAME=$(grep '^deb ' /etc/apt/sources.list | head -n1 | awk '{ print $3 }')
fi
# complain if no result yet
if [ -z "$CODENAME" ]; then
    cat <<EOF
Could not determine the distribution codename. Please report this as a bug to
pgsql-pkg-debian@postgresql.org. As a workaround, you can call this script with
the proper codename as parameter, e.g. "$0 squeeze".
EOF
    exit 1
fi

# errors are non-fatal above
set -eu

if [ "${HOST:-}" ]; then
    :
elif echo "$PG_REPOSITORY_DISTS" | grep -qw "$CODENAME"; then
    # known distribution on apt.postgresql.org
    HOST="apt.postgresql.org"
elif echo "$PG_ARCHIVE_DISTS" | grep -qw "$CODENAME"; then
    # known distribution on apt.postgresql.org
    HOST="apt-archive.postgresql.org"
else # unknown distribution, verify on the web
    HOST="apt.postgresql.org"
	DISTURL="https://$HOST/pub/repos/apt/dists/"
	if [ -x /usr/bin/curl ]; then
	    DISTHTML=$(curl -s $DISTURL || :)
	elif [ -x /usr/bin/wget ]; then
	    DISTHTML=$(wget --quiet -O - $DISTURL || :)
	fi
	if [ "${DISTHTML:-}" ]; then
	    if ! echo "$DISTHTML" | grep -q "$CODENAME-$PGDG"; then
		cat <<EOF
Your system is using the distribution codename $CODENAME, but $CODENAME-$PGDG
does not seem to be a valid distribution on
$DISTURL

We abort the installation here. If you want to use a distribution different
from your system, you can call this script with an explicit codename, e.g.
"$0 precise".

For more information, refer to https://wiki.postgresql.org/wiki/Apt
or ask on the mailing list for assistance: pgsql-pkg-debian@postgresql.org
EOF
		exit 1
	    fi
	fi
fi

# keyring needs to be readable for apt
umask 022
# prefer .gpg keyring from postgresql-common
KEYRING="/usr/share/postgresql-common/pgdg/apt.postgresql.org.gpg"
# otherwise, use the .asc key
test -e $KEYRING || KEYRING="/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc"
echo "Using keyring $KEYRING"
# write .asc key to disk if not yet present
if ! test -e $KEYRING; then
    mkdir -p /usr/share/postgresql-common/pgdg
    cat > $KEYRING <<EOF
-----BEGIN PGP PUBLIC KEY BLOCK-----

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
=DA1T
-----END PGP PUBLIC KEY BLOCK-----
EOF
fi

for version in ${PGVERSION:-}; do
    # devel version comes from *-pgdg-snapshot (with lower default apt pinning priority)
    if dpkg --compare-versions $version ge "${PG_DEVEL_VERSION:-999}"; then
        COMPONENTS="$COMPONENTS $version" # devel component is likely empty, but add it to be sure
        DEVEL_COMPONENT="${DEVEL_COMPONENT:-} $version"
        PIN="-t $CODENAME-pgdg-snapshot"
    # beta version needs a different component
    elif dpkg --compare-versions $version ge "${PG_BETA_VERSION:-999}"; then
        COMPONENTS="$COMPONENTS $version"
    fi

    # select packages to install
    PACKAGES="${PACKAGES:-} postgresql-$version postgresql-server-dev-$version"
    case $version in
        8*|9*) PACKAGES="$PACKAGES postgresql-contrib-$version" ;;
    esac
done

echo "Writing $SOURCESLIST ..."
cat > $SOURCESLIST <<EOF
Types: $TYPES
URIs: https://$HOST/pub/repos/apt
Suites: $CODENAME-$PGDG
Components: $COMPONENTS
Signed-By: $KEYRING
EOF

# write a separate section for devel without main so we don't include all of snapshot
if [ "${DEVEL_COMPONENT:-}" ]; then
cat >> $SOURCESLIST <<EOF

Types: $TYPES
URIs: https://$HOST/pub/repos/apt
Suites: $CODENAME-pgdg-snapshot
Components: ${DEVEL_COMPONENT# }
Signed-By: $KEYRING
EOF
fi

if [ "$SOURCESLIST" = "/etc/apt/sources.list.d/pgdg.sources" ]; then
    # remove pgdg.list when upgrading to pgdg.sources
    rm -vf /etc/apt/sources.list.d/pgdg.list /etc/apt/trusted.gpg.d/apt.postgresql.org.gpg
fi

echo
echo "Running apt-get update ..."
apt-get update

cat <<EOF

You can now start installing packages from $HOST.

Have a look at https://wiki.postgresql.org/wiki/Apt for more information;
most notably the FAQ at https://wiki.postgresql.org/wiki/Apt/FAQ
EOF

# remove/install packages
export DEBIAN_FRONTEND=noninteractive
if [ "${PURGE:-}" ]; then
    echo
    echo "Purging existing PostgreSQL packages ..."
    apt-get -y purge postgresql-client-common
fi
if [ "${INSTALL:-}" ]; then
    echo
    echo "Installing packages for PostgreSQL $PGVERSION ..."
    apt-get -y -o DPkg::Options::=--force-confnew \
        install ${PIN:-} $PACKAGES
fi
