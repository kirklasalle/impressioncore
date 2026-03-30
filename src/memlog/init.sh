#!/bin/bash
# Initialize memlog directory structure

mkdir -p /d:/Projects/impressioncore/memlog/state
mkdir -p /d:/Projects/impressioncore/memlog/tasks
mkdir -p /d:/Projects/impressioncore/memlog/persistence
mkdir -p /d:/Projects/impressioncore/memlog/changelogs

echo "Initialized memlog directory structure at $(date)" > /d:/Projects/impressioncore/memlog/state/init.log
