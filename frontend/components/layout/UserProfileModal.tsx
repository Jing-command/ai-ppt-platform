'use client';

/**
 * @fileoverview 用户信息弹窗组件
 * @author Frontend Agent
 * @date 2026-02-15
 */

import {useState, useRef, useEffect} from 'react';
import {motion, AnimatePresence} from 'framer-motion';
import {Camera, User, Mail, Save, X} from 'lucide-react';
import {updateUser, uploadAvatar, updateStoredUser} from '@/lib/api/auth';
import {User as UserType} from '@/types/auth';

interface UserProfileModalProps {
  user: UserType;
  isOpen: boolean;
  onClose: () => void;
  onUserUpdate?: (user: UserType) => void;
}

export function UserProfileModal({
  user,
  isOpen,
  onClose,
  onUserUpdate,
}: UserProfileModalProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [name, setName] = useState(user.name || '');
  const [avatarPreview, setAvatarPreview] = useState(user.avatar || '');
  const [isUploading, setIsUploading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState('');

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen) {
      setName(user.name || '');
      setAvatarPreview(user.avatar || '');
      setIsEditing(false);
      setError('');
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return () => {
      document.body.style.overflow = '';
    };
  }, [isOpen, user.name, user.avatar]);

  const handleAvatarClick = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setError('仅支持 jpg, png, gif, webp 格式');
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setError('文件大小不能超过 2MB');
      return;
    }

    const reader = new FileReader();
    reader.onload = (event) => {
      setAvatarPreview(event.target?.result as string);
    };
    reader.readAsDataURL(file);

    setIsUploading(true);
    setError('');

    try {
      const response = await uploadAvatar(file);
      const updatedUser = {...user, avatar: response.avatarUrl};
      updateStoredUser(updatedUser);
      onUserUpdate?.(updatedUser);
      setAvatarPreview(response.avatarUrl);
    } catch (err) {
      setError('上传头像失败，请重试');
      console.error('Upload avatar error:', err);
    } finally {
      setIsUploading(false);
    }
  };

  const handleSave = async () => {
    if (!name.trim()) {
      setError('用户名不能为空');
      return;
    }

    setIsSaving(true);
    setError('');

    try {
      const updatedUser = await updateUser({name: name.trim()});
      updateStoredUser(updatedUser);
      onUserUpdate?.(updatedUser);
      setIsEditing(false);
    } catch (err) {
      setError('保存失败，请重试');
      console.error('Update user error:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setName(user.name || '');
    setAvatarPreview(user.avatar || '');
    setIsEditing(false);
    setError('');
  };

  const renderAvatar = () => {
    if (avatarPreview) {
      return (
        <img
          src={avatarPreview}
          alt="Avatar"
          className="w-full h-full object-cover"
        />
      );
    }
    return (
      <span className="text-2xl font-semibold">
        {user.name?.[0]?.toUpperCase() || user.email?.[0]?.toUpperCase() || 'U'}
      </span>
    );
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <div className="fixed inset-0 z-[9999] flex items-center justify-center p-4">
          <motion.div
            initial={{opacity: 0}}
            animate={{opacity: 1}}
            exit={{opacity: 0}}
            transition={{duration: 0.2}}
            className="absolute inset-0 bg-black/60 backdrop-blur-sm"
            onClick={onClose}
          />

          <motion.div
            initial={{opacity: 0, scale: 0.9, y: 20}}
            animate={{opacity: 1, scale: 1, y: 0}}
            exit={{opacity: 0, scale: 0.9, y: 20}}
            transition={{type: 'spring', damping: 25, stiffness: 300}}
            className="relative w-full max-w-md bg-white rounded-2xl shadow-2xl overflow-hidden"
          >
            <div className="relative h-32 bg-gradient-to-br from-blue-500 via-indigo-500 to-purple-600">
              <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmZmZmYiIGZpbGwtb3BhY2l0eT0iMC4xIj48cGF0aCBkPSJNMzYgMzRjMC0yIDItNCAyLTRzLTItMi00LTItNCAyLTQgMiAyIDQgMiA0LTIgNC0yeiIvPjwvZz48L2c+PC9zdmc+')] opacity-30" />
              <button
                onClick={onClose}
                className="absolute top-4 right-4 p-2 text-white/80 hover:text-white hover:bg-white/20 rounded-full transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <div className="relative px-6 pb-6">
              <div className="flex justify-center -mt-14 mb-4">
                <div className="relative group">
                  <div className="w-28 h-28 rounded-full bg-gradient-to-br from-blue-400 to-indigo-500 flex items-center justify-center text-white overflow-hidden border-4 border-white shadow-xl ring-4 ring-gray-100">
                    {isUploading ? (
                      <div className="w-full h-full flex items-center justify-center bg-gray-100">
                        <div className="w-8 h-8 border-3 border-blue-500 border-t-transparent rounded-full animate-spin" />
                      </div>
                    ) : (
                      renderAvatar()
                    )}
                  </div>
                  <button
                    onClick={handleAvatarClick}
                    disabled={isUploading}
                    className="absolute bottom-1 right-1 p-2.5 bg-white rounded-full shadow-lg border border-gray-100 text-blue-600 hover:bg-blue-50 hover:scale-110 transition-all disabled:opacity-50"
                  >
                    <Camera className="w-4 h-4" />
                  </button>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/jpeg,image/png,image/gif,image/webp"
                    onChange={handleFileChange}
                    className="hidden"
                  />
                </div>
              </div>

              <div className="text-center mb-6">
                <h2 className="text-xl font-bold text-gray-900">
                  {user.name || '用户'}
                </h2>
                <p className="text-sm text-gray-500 mt-1">{user.email}</p>
              </div>

              {error && (
                <motion.div
                  initial={{opacity: 0, y: -10}}
                  animate={{opacity: 1, y: 0}}
                  className="mb-4 p-3 bg-red-50 text-red-600 text-sm rounded-xl border border-red-100"
                >
                  {error}
                </motion.div>
              )}

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    用户名
                  </label>
                  {isEditing ? (
                    <input
                      type="text"
                      value={name}
                      onChange={(e) => setName(e.target.value)}
                      className="w-full px-4 py-3 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all bg-gray-50 focus:bg-white"
                      placeholder="请输入用户名"
                    />
                  ) : (
                    <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl">
                      <User className="w-5 h-5 text-gray-400" />
                      <span className="text-gray-900">{user.name || '未设置'}</span>
                    </div>
                  )}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    邮箱地址
                  </label>
                  <div className="flex items-center gap-3 px-4 py-3 bg-gray-50 rounded-xl">
                    <Mail className="w-5 h-5 text-gray-400" />
                    <span className="text-gray-900">{user.email}</span>
                  </div>
                </div>
              </div>

              <div className="mt-6 flex gap-3">
                {isEditing ? (
                  <>
                    <button
                      onClick={handleCancel}
                      disabled={isSaving}
                      className="flex-1 px-4 py-3 border border-gray-200 text-gray-700 rounded-xl hover:bg-gray-50 transition-colors disabled:opacity-50 font-medium"
                    >
                      取消
                    </button>
                    <button
                      onClick={handleSave}
                      disabled={isSaving}
                      className="flex-1 flex items-center justify-center gap-2 px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all disabled:opacity-50 font-medium shadow-lg shadow-blue-500/25"
                    >
                      {isSaving ? (
                        <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <Save className="w-4 h-4" />
                      )}
                      保存修改
                    </button>
                  </>
                ) : (
                  <button
                    onClick={() => setIsEditing(true)}
                    className="w-full px-4 py-3 bg-gradient-to-r from-blue-500 to-indigo-500 text-white rounded-xl hover:from-blue-600 hover:to-indigo-600 transition-all font-medium shadow-lg shadow-blue-500/25"
                  >
                    编辑个人资料
                  </button>
                )}
              </div>
            </div>
          </motion.div>
        </div>
      )}
    </AnimatePresence>
  );
}
