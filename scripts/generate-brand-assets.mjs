import { writeFileSync, renameSync, unlinkSync, statSync, existsSync } from 'node:fs';
import sharp from 'sharp';

const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">
  <rect width="32" height="32" rx="6" fill="#0a7c8c"/>
  <path fill="#f4f1ea" d="M9 7h3.4v11.2c0 2.9 1.5 4.5 3.6 4.5s3.6-1.6 3.6-4.5V7H23v11.4c0 5-2.9 7.8-7 7.8s-7-2.8-7-7.8V7z"/>
</svg>`;

const sizes = [16, 32, 48];
const pngs = [];

for (const size of sizes) {
	const buf = await sharp(Buffer.from(svg)).resize(size, size).png().toBuffer();
	pngs.push(buf);
	await sharp(buf).toFile(`public/favicon-${size}.png`);
}

await sharp(Buffer.from(svg)).resize(180, 180).png().toFile('public/apple-touch-icon.png');

function createIco(pngBuffers) {
	const count = pngBuffers.length;
	const headerSize = 6 + count * 16;
	let dataOffset = headerSize;
	const total = headerSize + pngBuffers.reduce((n, b) => n + b.length, 0);
	const buf = Buffer.alloc(total);

	buf.writeUInt16LE(0, 0);
	buf.writeUInt16LE(1, 2);
	buf.writeUInt16LE(count, 4);

	let entryOffset = 6;
	for (const png of pngBuffers) {
		const w = png.readUInt32BE(16);
		const h = png.readUInt32BE(20);
		buf[entryOffset] = w >= 256 ? 0 : w;
		buf[entryOffset + 1] = h >= 256 ? 0 : h;
		buf[entryOffset + 2] = 0;
		buf[entryOffset + 3] = 0;
		buf.writeUInt16LE(1, entryOffset + 4);
		buf.writeUInt16LE(32, entryOffset + 6);
		buf.writeUInt32LE(png.length, entryOffset + 8);
		buf.writeUInt32LE(dataOffset, entryOffset + 12);
		png.copy(buf, dataOffset);
		entryOffset += 16;
		dataOffset += png.length;
	}
	return buf;
}

writeFileSync('public/favicon.ico', createIco(pngs));

const source = existsSync('public/og.jpg') ? 'public/og.jpg' : 'public/og.png';
await sharp(source)
	.resize(1200, 630, { fit: 'cover' })
	.jpeg({ quality: 82, mozjpeg: true })
	.toFile('public/og-tmp.jpg');
renameSync('public/og-tmp.jpg', 'public/og.jpg');
if (existsSync('public/og.png')) unlinkSync('public/og.png');

await sharp('public/og.jpg').jpeg({ quality: 84, mozjpeg: true }).toFile('public/twitter.jpg');

console.log('favicon + apple-touch ready');
console.log('og.jpg', Math.round(statSync('public/og.jpg').size / 1024), 'KB');
console.log('twitter.jpg', Math.round(statSync('public/twitter.jpg').size / 1024), 'KB');
