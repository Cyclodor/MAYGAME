from PIL import Image, ImageDraw
from pathlib import Path


def create_shield_swords_icon(output_path: Path) -> None:
	output_path.parent.mkdir(parents=True, exist_ok=True)

	# Base canvas (largest size), will be resized down to multi-res ICO
	base_size = 256
	img = Image.new("RGBA", (base_size, base_size), (0, 0, 0, 0))
	draw = ImageDraw.Draw(img)

	# Colors
	steel = (200, 205, 210, 255)
	steel_dark = (120, 125, 130, 255)
	leather = (120, 60, 30, 255)
	gold = (212, 175, 55, 255)
	shield_fill = (60, 70, 90, 255)
	shield_edge = (30, 35, 50, 255)

	# Draw shield (a rounded vertical shape)
	margin = 30
	left = margin
	right = base_size - margin
	top = margin
	bottom = base_size - margin
	# Outer shield
	draw.rounded_rectangle([left, top, right, bottom], radius=40, fill=shield_fill, outline=shield_edge, width=10)
	# Inner inset
	inner_margin = 20
	draw.rounded_rectangle([left + inner_margin, top + inner_margin, right - inner_margin, bottom - inner_margin], radius=30, outline=gold, width=6)

	# Crossed swords behind shield (visible above and around)
	# We'll draw blades first (diagonals), then hilts/guards
	blade_width = 14
	# Sword 1 (\) from top-left to bottom-right
	draw.line([(60, 40), (196, 176)], fill=steel, width=blade_width)
	draw.line([(60, 40), (196, 176)], fill=steel_dark, width=2)
	# Sword 2 (/) from top-right to bottom-left
	draw.line([(196, 40), (60, 176)], fill=steel, width=blade_width)
	draw.line([(196, 40), (60, 176)], fill=steel_dark, width=2)

	# Simple guards (small rectangles) and pommels (circles)
	guard_len = 50
	guard_w = 12
	# Guard for sword 1 near (90, 70)
	draw.rectangle([90 - guard_len // 2, 70 - guard_w // 2, 90 + guard_len // 2, 70 + guard_w // 2], fill=gold)
	# Guard for sword 2 near (166, 70)
	draw.rectangle([166 - guard_len // 2, 70 - guard_w // 2, 166 + guard_len // 2, 70 + guard_w // 2], fill=gold)

	# Handles
	draw.line([(80, 30), (95, 65)], fill=leather, width=blade_width)
	draw.line([(176, 30), (161, 65)], fill=leather, width=blade_width)

	# Pommels
	draw.ellipse([72 - 10, 22 - 10, 72 + 10, 22 + 10], fill=gold)
	draw.ellipse([184 - 10, 22 - 10, 184 + 10, 22 + 10], fill=gold)

	# Save multi-resolution ICO
	sizes = [16, 24, 32, 48, 64, 128, 256]
	imgs = [img.resize((s, s), Image.LANCZOS) for s in sizes]
	imgs[0].save(output_path, sizes=[(s, s) for s in sizes])


if __name__ == "__main__":
	out = Path("assets/icons/shield_swords.ico")
	create_shield_swords_icon(out)
	print(f"Icon generated: {out}")



