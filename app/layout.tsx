import type { Metadata } from 'next';
import './globals.css';
export const metadata: Metadata = {
  title: 'Omagym · Build your next skill',
  description: 'Practice languages and frameworks, generate weekend projects, and learn with a feedback-only coach.',
};
export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="en" className="dark"><body>{children}</body></html>;
}
