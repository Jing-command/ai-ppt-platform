'use client';

import {useEffect, useState} from 'react';
import {useRouter, useParams} from 'next/navigation';
import {motion} from 'framer-motion';
import {
  ChevronLeft,
  Save,
  Plus,
  Trash2,
  ArrowUp,
  ArrowDown,
  Sparkles,
  Type,
  Layout,
  BarChart3,
  Check
} from 'lucide-react';
import {
  getOutline,
  updateOutline,
  createPresentationFromOutline
} from '@/lib/api/outlines';
import {
  OutlineResponse,
  OutlineSection,
  PageType
} from '@/types/outline';

const pageTypeOptions: { type: PageType; label: string; icon: React.ElementType }[] = [
  {type: 'title', label: 'Title', icon: Type},
  {type: 'content', label: 'Content', icon: Type},
  {type: 'section', label: 'Section', icon: Layout},
  {type: 'chart', label: 'Chart', icon: BarChart3},
  {type: 'conclusion', label: 'Conclusion', icon: Check}
];

export default function OutlineEditPage() {
  const router = useRouter();
  const params = useParams();
  const outlineId = params.id as string;

  const [outline, setOutline] = useState<OutlineResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [activePageId, setActivePageId] = useState<string | null>(null);

  useEffect(() => {
    loadOutline();
  }, [outlineId]);

  const loadOutline = async () => {
    try {
      const data = await getOutline(outlineId);
      setOutline(data);
      if (data.pages?.length > 0 && !activePageId) {
        setActivePageId(data.pages[0].id);
      }
    } catch (error) {
      console.error('Failed to load outline:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSave = async () => {
    if (!outline) { return; }

    setIsSaving(true);
    try {
      await updateOutline(outlineId, {
        title: outline.title,
        description: outline.description,
        pages: outline.pages
      });
    } catch (error) {
      console.error('Failed to save outline:', error);
    } finally {
      setIsSaving(false);
    }
  };

  const handleAddPage = () => {
    if (!outline) { return; }

    const newPage: OutlineSection = {
      id: `temp-${Date.now()}`,
      pageNumber: outline.pages.length + 1,
      title: 'New Page',
      content: '',
      pageType: 'content'
    };

    const updatedPages = [...outline.pages, newPage];
    updatedPages.forEach((p, i) => {
      p.pageNumber = i + 1;
    });

    setOutline({...outline, pages: updatedPages, totalSlides: updatedPages.length});
    setActivePageId(newPage.id);
  };

  const handleDeletePage = (pageId: string) => {
    if (!outline) { return; }

    const updatedPages = outline.pages.filter(p => p.id !== pageId);
    updatedPages.forEach((p, i) => {
      p.pageNumber = i + 1;
    });

    setOutline({...outline, pages: updatedPages, totalSlides: updatedPages.length});
    if (activePageId === pageId && updatedPages.length > 0) {
      setActivePageId(updatedPages[0].id);
    }
  };

  const handleUpdatePage = (pageId: string, updates: Partial<OutlineSection>) => {
    if (!outline) { return; }

    const updatedPages = outline.pages.map(p =>
      p.id === pageId ? {...p, ...updates} : p
    );

    setOutline({...outline, pages: updatedPages});
  };

  const handleMovePage = (pageId: string, direction: 'up' | 'down') => {
    if (!outline) { return; }

    const index = outline.pages.findIndex(p => p.id === pageId);
    if (
      (direction === 'up' && index === 0) ||
      (direction === 'down' && index === outline.pages.length - 1)
    ) {
      return;
    }

    const newIndex = direction === 'up' ? index - 1 : index + 1;
    const updatedPages = [...outline.pages];
    const [movedPage] = updatedPages.splice(index, 1);
    updatedPages.splice(newIndex, 0, movedPage);

    updatedPages.forEach((p, i) => {
      p.pageNumber = i + 1;
    });

    setOutline({...outline, pages: updatedPages});
  };

  const handleGeneratePPT = async () => {
    try {
      const response = await createPresentationFromOutline(outlineId, {
        title: outline?.title,
        generateContent: true
      });
      router.push(`/app/presentations/${response.presentationId}/edit`);
    } catch (error) {
      console.error('Failed to generate PPT:', error);
    }
  };

  const activePage = outline?.pages.find(p => p.id === activePageId);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!outline) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-[var(--color-text-muted)]">Outline not found</p>
      </div>
    );
  }

  return (
    <div className="h-screen flex flex-col bg-[var(--color-background)]">
      <header className="h-14 bg-white border-b border-[var(--color-border)] flex items-center justify-between px-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <button
            onClick={() => router.push('/app/outlines')}
            className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
          >
            <ChevronLeft className="w-5 h-5 text-[var(--color-text)]" />
          </button>
          <div>
            <input
              type="text"
              value={outline.title}
              onChange={(e) => setOutline({...outline, title: e.target.value})}
              className="font-medium text-[var(--color-text)] bg-transparent border-none focus:outline-none focus:ring-2 focus:ring-blue-500 rounded px-2 py-1 -ml-2"
            />
            <p className="text-xs text-[var(--color-text-muted)]">{outline.pages.length} pages</p>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={handleSave}
            disabled={isSaving}
            className="flex items-center gap-2 px-3 py-1.5 border border-[var(--color-border)] rounded-lg hover:bg-[var(--color-surface)] transition-colors"
          >
            <Save className="w-4 h-4" />
            {isSaving ? 'Saving...' : 'Save'}
          </button>
          <button
            onClick={handleGeneratePPT}
            className="flex items-center gap-2 px-3 py-1.5 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-lg hover:opacity-90 transition-opacity"
          >
            <Sparkles className="w-4 h-4" />
            Generate PPT
          </button>
        </div>
      </header>

      <div className="flex-1 flex overflow-hidden">
        <aside className="w-72 bg-white border-r border-[var(--color-border)] flex flex-col">
          <div className="p-3 border-b border-[var(--color-border)] flex items-center justify-between">
            <h3 className="text-sm font-medium text-[var(--color-text)]">Pages</h3>
            <button
              onClick={handleAddPage}
              className="p-1.5 hover:bg-[var(--color-surface)] rounded-lg transition-colors"
            >
              <Plus className="w-4 h-4 text-blue-600" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {outline.pages.map((page, index) => (
              <motion.div
                key={page.id}
                layout
                onClick={() => setActivePageId(page.id)}
                className={`group flex items-center gap-2 p-2 rounded-lg cursor-pointer transition-colors ${
                  activePageId === page.id
                    ? 'bg-blue-50 border border-blue-200'
                    : 'hover:bg-[var(--color-surface)] border border-transparent'
                }`}
              >
                <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-100 text-blue-600 text-xs font-medium flex items-center justify-center">
                  {page.pageNumber}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium text-[var(--color-text)] truncate">{page.title}</p>
                  <p className="text-xs text-[var(--color-text-muted)] truncate">{page.pageType || 'content'}</p>
                </div>
                <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity"
                >
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMovePage(page.id, 'up');
                    }}
                    disabled={index === 0}
                    className="p-1 hover:bg-white rounded disabled:opacity-30"
                  >
                    <ArrowUp className="w-3 h-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleMovePage(page.id, 'down');
                    }}
                    disabled={index === outline.pages.length - 1}
                    className="p-1 hover:bg-white rounded disabled:opacity-30"
                  >
                    <ArrowDown className="w-3 h-3" />
                  </button>
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleDeletePage(page.id);
                    }}
                    className="p-1 hover:bg-red-50 rounded"
                  >
                    <Trash2 className="w-3 h-3 text-red-500" />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        </aside>

        <main className="flex-1 bg-[var(--color-surface)] p-8 overflow-y-auto">
          {activePage ? (
            <motion.div
              initial={{opacity: 0, y: 20}}
              animate={{opacity: 1, y: 0}}
              className="max-w-3xl mx-auto bg-white rounded-xl shadow-lg p-8"
            >
              <div className="space-y-6">
                <div className="flex items-center gap-2 text-sm text-[var(--color-text-muted)]">
                  <span className="px-2 py-1 bg-blue-100 text-blue-600 rounded font-medium">
                    Page {activePage.pageNumber}
                  </span>                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Title
                  </label>
                  <input
                    type="text"
                    value={activePage.title}
                    onChange={(e) => handleUpdatePage(activePage.id, {title: e.target.value})}
                    className="w-full px-4 py-3 text-lg font-medium bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                    placeholder="Enter page title..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Page Type
                  </label>
                  <div className="grid grid-cols-5 gap-2">
                    {pageTypeOptions.map((option) => {
                      const Icon = option.icon;
                      const isActive = activePage.pageType === option.type;
                      return (
                        <button
                          key={option.type}
                          onClick={() => handleUpdatePage(activePage.id, {pageType: option.type})}
                          className={`flex flex-col items-center gap-2 p-3 rounded-lg border text-sm transition-colors ${
                            isActive
                              ? 'border-blue-500 bg-blue-50 text-blue-600'
                              : 'border-[var(--color-border)] hover:bg-[var(--color-surface)]'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          {option.label}
                        </button>
                      );
                    })}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Content
                  </label>
                  <textarea
                    value={activePage.content || ''}
                    onChange={(e) => handleUpdatePage(activePage.id, {content: e.target.value})}
                    rows={8}
                    className="w-full px-4 py-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors resize-none"
                    placeholder="Enter page content..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Notes
                  </label>
                  <textarea
                    value={activePage.notes || ''}
                    onChange={(e) => handleUpdatePage(activePage.id, {notes: e.target.value})}
                    rows={3}
                    className="w-full px-4 py-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors resize-none"
                    placeholder="Add notes (optional)..."
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                    Image Prompt (for AI generation)
                  </label>
                  <input
                    type="text"
                    value={activePage.imagePrompt || ''}
                    onChange={(e) => handleUpdatePage(activePage.id, {imagePrompt: e.target.value})}
                    className="w-full px-4 py-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-[var(--color-text)] focus:outline-none focus:border-[var(--color-primary)] transition-colors"
                    placeholder="Describe the image you want..."
                  />
                </div>
              </div>
            </motion.div>
          ) : (
            <div className="flex flex-col items-center justify-center h-full text-[var(--color-text-muted)]">
              <Plus className="w-12 h-12 mb-4 opacity-50" />
              <p>Click Add Page to start editing</p>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
