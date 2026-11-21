import { useRef, useEffect } from 'react';
import { ChatMessage } from '../chat-store';

export const STARTER_PROMPTS = [
  "Tạo landing page cho studio chụp ảnh phong cách tối giản có bảng giá và form đặt lịch",
  "Tạo SaaS dashboard thống kê doanh thu với bảng dữ liệu dự án và metrics cards",
  "Đổi tiêu đề hero sang phong cách sang trọng và thêm nút Đăng ký ngay"
];

export function useMessageListStore(messages: ChatMessage[]) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  return {
    messagesEndRef,
    starterPrompts: STARTER_PROMPTS,
  };
}
