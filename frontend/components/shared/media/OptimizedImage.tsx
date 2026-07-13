"use client"

import Image from "next/image"
import { useState } from "react"
import { ImageIcon } from "lucide-react"

interface OptimizedImageProps {
  src: string | null | undefined
  alt: string
  className?: string
  fill?: boolean
  width?: number
  height?: number
}

export function OptimizedImage({ 
  src, 
  alt, 
  className = "rounded-lg", 
  fill = false,
  width = 400,
  height = 300
}: OptimizedImageProps) {
  const [hasError, setHasError] = useState(false)

  // Если картинки нет или она не загрузилась, показываем заглушку
  if (!src || hasError) {
    return (
      <div className={`bg-gray-100 flex items-center justify-center ${fill ? "w-full h-full" : ""}`} style={fill ? {} : { width, height }}>
        <ImageIcon className="h-12 w-12 text-gray-300" />
      </div>
    )
  }

  if (fill) {
    return (
      <Image
        src={src}
        alt={alt}
        fill
        className={`object-cover transition-opacity duration-300 ${className}`}
        sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        onError={() => setHasError(true)}
        priority={false} // Измените на true, если это главное изображение страницы (LCP)
      />
    )
  }

  return (
    <Image
      src={src}
      alt={alt}
      width={width}
      height={height}
      className={`object-cover transition-opacity duration-300 ${className}`}
      onError={() => setHasError(true)}
    />
  )
}
