"""Keep untranslated X originals out of public data without blocking site publication."""
import json
import pathlib
from x_archive import readable_post

ROOT = pathlib.Path(__file__).resolve().parents[1]
PUBLIC_DATA = ROOT / 'public' / 'data'
REVIEW_QUEUE = ROOT / 'state' / 'x-language-review.json'


def untranslated(posts):
    return [
        post for post in posts
        if not readable_post(post)
        or (
            post.get('originalLanguage') != 'sv'
            and post.get('swedish', {}).get('method') != 'translation'
        )
    ]


def main():
    held_by_id = {}
    published_counts = {}

    for name in ('x.json', 'x-archive.json'):
        path = PUBLIC_DATA / name
        data = json.loads(path.read_text(encoding='utf-8'))
        posts = data.get('posts', [])
        held = untranslated(posts)

        for post in held:
            post_id = post.get('id')
            if not isinstance(post_id, str):
                continue
            held_by_id[post_id] = {
                'id': post_id,
                'sourceUrl': post.get('url', ''),
                'originalLanguage': post.get('originalLanguage', 'und'),
                'text': post.get('text', ''),
                'reason': 'needs_swedish_translation',
            }

        data['posts'] = [post for post in posts if post not in held]
        temporary = path.with_suffix('.tmp')
        temporary.write_text(
            json.dumps(data, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )
        temporary.replace(path)
        published_counts[name] = len(data['posts'])

    # Keep every withheld public X post available for editorial follow-up as a
    # workflow artifact. The source text is never copied into the deployed feed.
    if held_by_id:
        REVIEW_QUEUE.parent.mkdir(parents=True, exist_ok=True)
        try:
            queue = json.loads(REVIEW_QUEUE.read_text(encoding='utf-8'))
        except (OSError, ValueError):
            queue = {}
        existing = {
            item.get('id'): item
            for item in queue.get('items', [])
            if isinstance(item, dict) and isinstance(item.get('id'), str)
        }
        existing.update(held_by_id)
        queue['items'] = list(existing.values())
        queue['counts'] = {**queue.get('counts', {}), 'pending': len(queue['items'])}
        REVIEW_QUEUE.write_text(
            json.dumps(queue, ensure_ascii=False, indent=2) + '\n',
            encoding='utf-8',
        )

    print(
        'X-publicering kontrollerad: '
        + json.dumps({
            'published': published_counts,
            'withheldForSwedishTranslation': len(held_by_id),
        }, ensure_ascii=False),
        flush=True,
    )


if __name__ == '__main__':
    main()
