import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Saint Prototype",
  description: "Goal-to-contextual-path prototype for Saint.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
