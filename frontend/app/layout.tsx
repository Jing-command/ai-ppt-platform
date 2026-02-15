import type {Metadata} from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'AI PPT Platform',
  description: '智能演示文稿生成平台'
};

export default function RootLayout({
  children
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
