'use client';

import {motion} from 'framer-motion';
import {Slide, SlideType} from '@/types/presentation';

interface SlideThumbnailProps {
  slide: Slide;
  index: number;
  isActive: boolean;
  onClick: () => void;
}

const slideTypeLabels: Record<SlideType, string> = {
    title: '封面',
    content: '内容',
    section: '章节',
    chart: '图表',
    conclusion: '总结'
};

const slideTypeColors: Record<SlideType, string> = {
    title: 'bg-purple-100 text-purple-700 border-purple-300',
    content: 'bg-blue-100 text-blue-700 border-blue-300',
    section: 'bg-orange-100 text-orange-700 border-orange-300',
    chart: 'bg-green-100 text-green-700 border-green-300',
    conclusion: 'bg-gray-100 text-gray-700 border-gray-300'
};

export default function SlideThumbnail({
    slide,
    index,
    isActive,
    onClick
}: SlideThumbnailProps) {
    const getPreviewContent = () => {
        const {content} = slide;

        switch (slide.type) {
        case 'title':
            return (
                <div className="text-center">
                    <div className="font-bold text-xs truncate px-2">{content.title || '标题'}</div>
                    {content.subtitle && (
                        <div className="text-[8px] text-gray-500 truncate px-2 mt-0.5">{content.subtitle}</div>
                    )}
                </div>
            );
        case 'content':
            return (
                <div className="px-2">
                    <div className="font-semibold text-[10px] truncate mb-1">{content.title || '内容页'}</div>
                    {content.bullets && content.bullets.length > 0 ? (
                        <ul className="space-y-0.5">
                            {content.bullets.slice(0, 3).map((bullet, i) => (
                                <li key={i} className="text-[7px] text-gray-600 truncate flex items-start gap-0.5">
                                    <span className="mt-0.5">•</span>
                                    <span className="truncate">{bullet}</span>
                                </li>
                            ))}
                            {content.bullets.length > 3 && (
                                <li className="text-[7px] text-gray-400">...</li>
                            )}
                        </ul>
                    ) : content.text ? (
                        <div className="text-[7px] text-gray-600 line-clamp-3">{content.text}</div>
                    ) : null}
                </div>
            );
        case 'section':
            return (
                <div className="text-center px-2">
                    <div className="font-bold text-sm">§</div>
                    <div className="font-semibold text-[10px] truncate">{content.title || '章节'}</div>
                </div>
            );
        case 'chart':
            return (
                <div className="px-2">
                    <div className="font-semibold text-[10px] truncate mb-1">{content.title || '图表'}</div>
                    <div className="flex items-end justify-center gap-1 h-8 mt-2">
                        {[40, 70, 50, 80, 60].map((h, i) => (
                            <div
                                key={i}
                                className="w-2 bg-blue-400 rounded-t"
                                style={{height: `${h}%`}}
                            />
                        ))}
                    </div>
                </div>
            );
        case 'conclusion':
            return (
                <div className="text-center px-2">
                    <div className="font-bold text-lg">✓</div>
                    <div className="font-semibold text-[10px] truncate">{content.title || '总结'}</div>
                </div>
            );
        default:
            return (
                <div className="text-center text-[10px] text-gray-400">
            第 {index + 1} 页
                </div>
            );
        }
    };

    return (
        <motion.button
            onClick={onClick}
            whileHover={{scale: 1.02}}
            whileTap={{scale: 0.98}}
            className={`
        w-full text-left group relative
        transition-all duration-200
        ${isActive ? 'ring-2 ring-blue-500 ring-offset-2' : 'hover:shadow-md'}
      `}
        >
            {/* 幻灯片编号 */}
            <div className="flex items-center gap-2 mb-1">
                <span className={`
          text-xs font-medium px-1.5 py-0.5 rounded
          ${isActive ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-600'}
        `}>
                    {index + 1}
                </span>
                <span className={`
          text-[10px] px-1.5 py-0.5 rounded border
          ${slideTypeColors[slide.type]}
        `}
                >
                    {slideTypeLabels[slide.type]}
                </span>
            </div>

            {/* 缩略图内容 */}
            <div
                className={`
          aspect-[4/3] rounded-lg border-2 overflow-hidden
          flex flex-col justify-center
          ${isActive
            ? 'border-blue-500 bg-blue-50'
            : 'border-gray-200 bg-white group-hover:border-gray-300'
        }
        `}
            >
                {getPreviewContent()}
            </div>

            {/* 悬停提示 */}
            <div className="mt-1 text-[10px] text-gray-500 truncate px-0.5">
                {slide.content.title || `幻灯片 ${index + 1}`}
            </div>
        </motion.button>
    );
}
