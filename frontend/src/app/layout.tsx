import type { Metadata } from "next";
import { Geist } from "next/font/google";
import { JetBrains_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
  display: "swap",
});

const jetbrainsMono = JetBrains_Mono({
  variable: "--font-jetbrains-mono",
  subsets: ["latin"],
  display: "swap",
  weight: ["400", "500", "600"],
});

export const metadata: Metadata = {
  title: "Claudio — Compilador Fuente-a-Fuente",
  description:
    "Explora el interior de un compilador paso a paso: analisis lexico, sintactico descendente recursivo, predictivo LL(1) y traduccion a Swift.",
  openGraph: {
    title: "Claudio — Compilador Fuente-a-Fuente",
    description:
      "IDE interactivo para explorar las fases de compilacion de un lenguaje con palabras clave en espanol.",
    type: "website",
    locale: "es_ES",
  },
  icons: { icon: "/favicon.ico" },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="es"
      className={`${geistSans.variable} ${jetbrainsMono.variable} h-full antialiased`}
    >
      <body className="min-h-dvh flex flex-col overflow-hidden font-sans">
        <a
          href="#main-content"
          className="sr-only focus:not-sr-only focus:absolute focus:z-[999] focus:top-2 focus:left-2 focus:px-4 focus:py-2 focus:rounded-md"
          style={{ backgroundColor: "var(--color-accent)", color: "var(--color-bg)" }}
        >
          Ir al contenido principal
        </a>
        {children}
      </body>
    </html>
  );
}
