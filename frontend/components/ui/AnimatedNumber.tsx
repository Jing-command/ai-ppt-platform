'use client';

import {useState, useEffect} from 'react';

interface AnimatedNumberProps {
  value: number;
  duration?: number;
}

export function AnimatedNumber({value, duration = 2}: AnimatedNumberProps) {
    const [displayValue, setDisplayValue] = useState(0);

    useEffect(() => {
        let startTime: number;
        let animationFrame: number;

        const animate = (currentTime: number) => {
            if (!startTime) { startTime = currentTime; }
            const progress = Math.min((currentTime - startTime) / (duration * 1000), 1);
            const easeOut = 1 - Math.pow(1 - progress, 3);
            setDisplayValue(Math.floor(easeOut * value));

            if (progress < 1) {
                animationFrame = requestAnimationFrame(animate);
            }
        };

        animationFrame = requestAnimationFrame(animate);
        return () => cancelAnimationFrame(animationFrame);
    }, [value, duration]);

    return <span>{displayValue}</span>;
}
