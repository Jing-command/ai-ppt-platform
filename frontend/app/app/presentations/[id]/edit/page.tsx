'use client';

import {useEffect, useState, useCallback} from 'react';
import {useRouter, useParams} from 'next/navigation';
import {motion, AnimatePresence} from 'framer-motion';
import {
  ChevronLeft,
  Save,
  Undo,
  Redo,
  Plus,
  Play,
  Download,
  Trash2,
  GripVertical,
  Type,
  BarChart3,
  Layout,
  Check,
  Sparkles,
  X
} from 'lucide-react';
import {
  getPresentation,
  updatePresentation,
  addSlide,
  updateSlide,
  deleteSlide,
  undoSlide,
  redoSlide
} from '@/lib/api/presentations';
import {
  PresentationDetailResponse,
  Slide,
  SlideType,
  SlideCreate,
  SlideUpdate
} from '@/types/presentation';

const slideTypeOptions: { type: SlideType; label: string; icon: React.ElementType }[] = [
  {type: 'title', label: 'Title', icon: Type},
  {type: 'content', label: 'Content', icon: Type},
  {type: 'section', label: 'Section', icon: Layout},
  {type: 'chart', label: 'Chart', icon: BarChart3},
  {type: 'conclusion', label: 'Conclusion', icon: Check}
];

const themeOptions = [
  {id: 'default', name: 'Default', primary: '#2563eb', bg: '#ffffff'},
  {id: 'dark', name: 'Dark', primary: '#3b82f6', bg: '#1e293b'},
  {id: 'warm', name: 'Warm', primary: '#f59e0b', bg: '#fff7ed'},
  {id: 'nature', name: 'Nature', primary: '#10b981', bg: '#f0fdf4'},
  {id: 'elegant', name: 'Elegant', primary: '#8b5cf6', bg: '#faf5ff'}
];

export default function PresentationEditPage() {
  const router = useRouter();
  const params = useParams();
  const presentationId = params.id as string;

  const [presentation, setPresentation] = useState<PresentationDetailResponse | null>(null);
  const [slides, setSlides] = useState<Slide[]>([]);
  const [activeSlideId, setActiveSlideId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [showAddMenu, setShowAddMenu] = useState(false);
  const [canUndo, setCanUndo] = useState(false);
  const [canRedo, setCanRedo] = useState(false);

  const activeSlide = slides.find(s => s.id === activeSlideId);

  useEffect(() => {
    loadPresentation();
  }, [presentationId]);

  const loadPresentation = async () => {
    try {
      const data = await getPresentation(presentationId);
      setPresentation(data);
      setSlides(data.slides || []);
      if (data.slides?.length > 0 && !activeSlideId) {
        setActiveSlideId(data.slides[0].id);
      }
    } catch (error) {
      console.error('Failed to load presentation:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!presentation) { return; }

    setIsSaving(true);
    try {
      await updatePresentation(presentationId, {
        title: presentation.title,
        description: presentation.description,
        slides
      });
    } catch (error) {
      console.error('Failed to save presentation:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddSlide = async (type: SlideType = 'content') => {
    try {
      const newSlideData: SlideCreate = {
        type,
        content: {
          title: type === 'title' ? 'Title' : 'New Slide',
          text: type === 'content' ? 'Enter content here...' : ''
        }
      };

      const response = await addSlide(presentationId, newSlideData);
      setSlides(response.slides || []);
      const newSlide = response.slides?.[response.slides.length - 1];
      if (newSlide) {
        setActiveSlideId(newSlide.id);
      }
      setShowAddMenu(false);
    } catch (error) {
      console.error('Failed to add slide:', error);
    }
  };

  const handleUpdateSlide = async (slideId: string, updates: SlideUpdate) => {
    try {
      const updatedSlide = await updateSlide(presentationId, slideId, updates);
      setSlides(prev =>
        prev.map(s => s.id === slideId ? updatedSlide : s)
      );
      setCanUndo(true);
    } catch (error) {
      console.error('Failed to update slide:', error);
    }
  };

  const handleDeleteSlide = async (slideId: string) => {
    if (!confirm('Delete this slide?')) { return; }

    try {
      await deleteSlide(presentationId, slideId);
      setSlides(prev => {
        const newSlides = prev.filter(s => s.id !== slideId);
        if (activeSlideId === slideId && newSlides.length > 0) {
          setActiveSlideId(newSlides[0].id);
        }
        return newSlides;
      });
    } catch (error) {
      console.error('Failed to delete slide:', error);
    }
  };

  const handleUndo = async () => {
    if (!activeSlideId) { return; }
    try {
      const response = await undoSlide(presentationId, activeSlideId);
      if (response.success) {
        loadPresentation();
        setCanUndo(false);
        setCanRedo(true);
      }
    } catch (error) {
      console.error('Failed to undo:', error);
    }
  };

  const handleRedo = async () => {
    if (!activeSlideId) { return; }
    try {
      const response = await redoSlide(presentationId, activeSlideId);
      if (response.success) {
        loadPresentation();
        setCanUndo(true);
        setCanRedo(false);
      }
    } catch (error) {
      console.error('Failed to redo:', error);
    }
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!presentation) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-[var(--color-text-muted)]">Presentation not found</p>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--color-background)]">
      {/* Top Toolbar */}
      <header className="h-14 bg-white border-b border-[var(--color-border)] flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/app/presentations')}
            className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-[var(--color-text)]" />
          </button>
          <div>
            <input
              type="text"
              value={presentation.title}
              onChange={(e) => setPresentation({...presentation, title: e.target.value})}
              className="font-medium text-[var(--color-text)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 -ml-2"
            />
            <p className="text-xs text-[var(--color-text-muted)]">{slides.length} slides</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleUndo}
            disabled={!canUndo}
            className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors disabled:opacity-50"
          >
            <Undo className="w-5 h-5 text-[var(--color-text)]" />
          </button>
          <button
            onClick={handleRedo}
            disabled={!canRedo}
            className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors disabled:opacity-50"
          >
            <Redo className="w-5 h-5 text-[var(--color-text)]" />
          </button>
          <div className="w-px h-6 bg-[var(--color-border)] mx-2" />
          <button
            onClick={() => setShowAddMenu(!showAddMenu)}
            className="flex items-center gap-2 px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-4 h-4" />
            Add Slide
          </button>
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors">
            <Play className="w-4 h-4" />
            Preview
          </button>
          <button className="flex items-center gap-2 px-3 py-1.5 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
          >
            <Download className="w-4 h-4" />
            Export
          </button>
        </div>
      </header>

      {/* Main Editor Area */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Sidebar */}
        <aside className="w-64 bg-white border-r border-[var(--color-border)] flex flex-col">
          <div className="p-3 border-b border-[var(--color-border)]">
            <h3 className="text-sm font-medium text-[var(--color-text)]">Slides</h3>
          </div>
          <div className="flex-1 overflow-y-auto p-3 space-y-2">
            {slides.map((slide, index) => (
              <motion.div
                key={slide.id}
                layout
                onClick={() => setActiveSlideId(slide.id)}
                className={`relative group cursor-pointer rounded-lg border-2 overflow-hidden transition-all ${
                  activeSlideId === slide.id
                    ? 'border-blue-500 shadow-md'
                    : 'border-transparent hover:border-[var(--color-border)]'
                }`}
              >
                <div className="aspect-video bg-gradient-to-br from-blue-50 to-purple-50 flex items-center justify-center">
                  <span className="text-2xl font-bold text-blue-200">{index + 1}</span>
                </div>
                <div className="absolute top-1 left-1 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div className="p-1 bg-white rounded shadow cursor-grab">
                    <GripVertical className="w-3 h-3 text-gray-500" />
                  </div>
                </div>
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    handleDeleteSlide(slide.id);
                  }}
                  className="absolute top-1 right-1 p-1 bg-white rounded shadow opacity-0 group-hover:opacity-100 transition-opacity hover:bg-red-50"
                >
                  <Trash2 className="w-3 h-3 text-red-500" />
                </button>
              </motion.div>
            ))}
          </div>
        </aside>

        {/* Center */}
        <main className="flex-1 bg-[var(--color-surface)] flex flex-col items-center justify-center p-8">
          {activeSlide ? (
            <div className="w-full max-w-4xl aspect-video bg-white rounded-lg shadow-lg overflow-hidden flex flex-col">
              <div className="flex-1 p-12">
                <input
                  type="text"
                  value={activeSlide.content.title || ''}
                  onChange={(e) =>
                    handleUpdateSlide(activeSlide.id, {
                      content: {...activeSlide.content, title: e.target.value}
                    })
                  }
                  className="w-full text-4xl font-bold text-[var(--color-text)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded placeholder-gray-300"
                  placeholder="Enter title..."
                />
                <textarea
                  value={activeSlide.content.text || ''}
                  onChange={(e) =>
                    handleUpdateSlide(activeSlide.id, {
                      content: {...activeSlide.content, text: e.target.value}
                    })
                  }
                  className="w-full mt-6 text-lg text-[var(--color-text-secondary)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded resize-none placeholder-gray-300"
                  rows={6}
                  placeholder="Enter content here..."
                />
              </div>

              <div className="border-t border-[var(--color-border)] p-4 bg-gray-50">
                <p className="text-xs font-medium text-[var(--color-text-muted)] mb-2">Notes</p>
                <textarea
                  value={activeSlide.notes || ''}
                  onChange={(e) =>
                    handleUpdateSlide(activeSlide.id, {
                      notes: e.target.value
                    })
                  }
                  className="w-full text-sm text-[var(--color-text-secondary)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded resize-none"
                  rows={2}
                  placeholder="Add speaker notes..."
                />
              </div>
            </div>
          ) : (
            <div className="text-center">
              <Plus className="w-16 h-16 text-[var(--color-text-placeholder)] mx-auto mb-4" />
              <p className="text-[var(--color-text-muted)]">Click Add Slide to start creating</p>
            </div>
          )}
        </main>

        {/* Right Sidebar */}
        <aside className="w-72 bg-white border-l border-[var(--color-border)] flex flex-col">
          <div className="p-4 border-b border-[var(--color-border)]">
            <h3 className="text-sm font-medium text-[var(--color-text)]">Properties</h3>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            <div>
              <label className="text-sm font-medium text-[var(--color-text-secondary)] mb-2 block">
                Slide Type
              </label>
              <div className="grid grid-cols-2 gap-2">
                {slideTypeOptions.map((option) => {
                  const Icon = option.icon;
                  const isActive = activeSlide?.type === option.type;
                  return (
                    <button
                      key={option.type}
                      onClick={() =>
                        activeSlide &&
                        handleUpdateSlide(activeSlide.id, {type: option.type})
                      }
                      className={`flex items-center gap-2 p-2 rounded-lg border text-sm transition-colors ${
                        isActive
                          ? 'border-blue-500 bg-blue-50 text-blue-600'
                          : 'border-[var(--color-border)] hover:bg-[var(--color-surface)]'
                      }`}
                    >
                      <Icon className="w-4 h-4" />
                      {option.label}
                    </button>
                  );
                })}
              </div>
            </div>

            <div>
              <label className="text-sm font-medium text-[var(--color-text-secondary)] mb-2 block">
                Theme
              </label>
              <div className="space-y-2">
                {themeOptions.map((theme) => (
                  <button
                    key={theme.id}
                    className="flex items-center gap-3 w-full p-2 rounded-lg border border-[var(--color-border)] hover:bg-[var(--color-surface)] transition-colors"
                  >
                    <div
                      className="w-8 h-8 rounded-lg border"
                      style={{backgroundColor: theme.bg, borderColor: theme.primary}}
                    />
                    <span className="text-sm">{theme.name}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className="pt-4 border-t border-[var(--color-border)]">
              <button className="w-full flex items-center justify-center gap-2 p-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity">
                <Sparkles className="w-4 h-4" />
                AI Optimize
              </button>
            </div>
          </div>
        </aside>
      </div>

      {/* Add Slide Menu */}
      <AnimatePresence>
        {showAddMenu && (
          <>
            <div
              className="fixed inset-0 z-40"
              onClick={() => setShowAddMenu(false)}
            />
            <motion.div
              initial={{opacity: 0, y: -10}}
              animate={{opacity: 1, y: 0}}
              exit={{opacity: 0, y: -10}}
              className="absolute top-14 left-1/2 -translate-x-1/2 z-50 w-96 bg-white rounded-xl shadow-xl border border-[var(--color-border)] p-4"
            >
              <h3 className="text-sm font-medium text-[var(--color-text)] mb-3">Select Layout</h3>
              <div className="grid grid-cols-2 gap-3">
                {slideTypeOptions.map((option) => {
                  const Icon = option.icon;
                  return (
                    <button
                      key={option.type}
                      onClick={() => handleAddSlide(option.type)}
                      className="flex flex-col items-center gap-2 p-4 rounded-lg border border-[var(--color-border)] hover:border-blue-500 hover:bg-blue-50 transition-all"
                    >
                      <div className="w-12 h-12 rounded-lg bg-blue-100 flex items-center justify-center">
                        <Icon className="w-6 h-6 text-blue-600" />
                      </div>
                      <span className="text-sm font-medium">{option.label}</span>
                    </button>
                  );
                })}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </div>
  );
}
