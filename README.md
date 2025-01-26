## twitter-to-bsky importer

Import your Twitter archive into a Bluesky account.

!
!
!

**At this time, this will spam others timelines, so it is only recommended
to run on new accounts with no followers.** See `Known problems` below for details.


!
!
!

Usage:

```bash
# Get an archive from https://twitter.com/settings/download_your_data
# Unzip a Twitter archive so the assets/ folder is in the same directory as main.py
git clone https://github.com/ianklatzco/twitter-to-bsky.git
cd twitter-to-bsky
# Create virtual environment for python
python3 -m venv ./venv
# Install requirements
./venv/bin/pip install -r Requirements.txt
# Copy your twitter archive to ./data/
cp -r _pathToArchive_/data ./
# Use a space in front of the PASSWORD export to prevent it from going to your bash history
export BSKY_USERNAME="yourname.bsky.social"
 export PASSWORD="yourpassword"
./venv/bin/python3 main.py
```

### Known problems

Bluesky's UI currently renders timestamps based on the indexedAt field (i.e., when the bloot was blooted) rather than the createdAt field (when the bloot CLAIMS it was blooted).

The code here currently tries to post skoots with the old timestamps, but the Bluesky UI will not render them so. It used to, and then Paul probably patched the bug ^^

Does not preserve replies, so your threads will be decomposed into de-contextualized individual posts.

~~Does not convert links in the text of tweets.~~ Now converts links, including those to your own tweets!

Supports blooting only a single image tweet (multiple image tweets will be skipped) _(From @webash: the export I was testing with only had single image tweets))_

### Thanks to

- Boris Mann
- Shinya Kato
- [Heartade](https://github.com/Heartade)
- [WebAsh](https://github.com/WebAsh)

### See also

https://github.com/ianklatzco/atprototools -- underlying library
