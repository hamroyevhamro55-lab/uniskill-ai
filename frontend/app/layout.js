import "./globals.css";

export const metadata = {
  title: "UniSkill AI",
  description: "Talabaning kasbiy, raqamli va shaxsiy kompetensiyalarini aniqlash, rivojlantirish va tasdiqlash platformasi",
};

export default function RootLayout({ children }) {
  return (
    <html lang="uz">
      <body>{children}</body>
    </html>
  );
}
