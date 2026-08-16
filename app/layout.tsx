import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "EcoPark AI",
  description: "Preliminary ecological park planning",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="es">
      <body>{children}</body>
    </html>
  );
}
