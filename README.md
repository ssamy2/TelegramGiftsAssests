# Telegram Gift Images

Free collection of Telegram gift images in WebP format.

## Usage

All images are **free to use** for any purpose.

### Image URL Logic

**Upgraded Gifts (NFT):**
Use Fragment slug from the gift data:
```
https://nft.fragment.com/gift/{slug}.medium.jpg
```
Example: `https://nft.fragment.com/gift/plushpepe-2133.medium.jpg`

**Unupgraded Gifts:**
Use short_name from this repository:
```
https://cdn.jsdelivr.net/gh/ssamy2/TG_Photos@main/webp/by_name/{short_name}.webp
```
Example: `https://cdn.jsdelivr.net/gh/ssamy2/TG_Photos@main/webp/by_name/plush_pepe.webp`

### Short Name Convention

`short_name` is generated from `full_name`:
- Only English alphabetic letters (a-z)
- Lowercase only
- Underscores between words

Examples:
| Full Name | Short Name |
|-----------|------------|
| Plush Pepe | plush_pepe |
| B-Day Candle | bday_candle |
| Jack-in-the-Box | jackinthebox |
| Durov's Cap | durovs_cap |

## Files

- `webp/` - WebP image files (by ID and by short name)
  - `by_id/` - Named by gift ID
  - `by_name/` - Named by short name
- `tgs/` - TGS animation files (by ID and by short name)
  - `by_id/` - Named by gift ID
  - `by_name/` - Named by short name
- `Gifts_Details.json` - Full gift data with names and IDs

## Gift Data Structure

```json
{
  "upgraded": [
    {
      "full_name": "Plush Pepe",
      "short_name": "plush_pepe",
      "regular_id": "5936013938331222567"
    }
  ],
  "unupgraded": [
    {
      "full_name": "Torch",
      "short_name": "torch",
      "id": "5999277561060787166"
    }
  ]
}
```

## License

Free to use. No attribution required.
