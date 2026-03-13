import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  RefreshControl,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import api from '../../utils/api';
import { useAuth } from '../../contexts/AuthContext';

interface Feedback {
  feedback_id: string;
  user_name: string;
  category: string;
  title: string;
  description: string;
  upvotes: number;
  status: string;
  created_at: string;
  user_upvoted?: boolean;
}

export default function FeedbackScreen() {
  const { user } = useAuth();
  const [feedbacks, setFeedbacks] = useState<Feedback[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showForm, setShowForm] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  // Form state
  const [category, setCategory] = useState('feature');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');

  const categories = [
    { id: 'bug', label: 'Bug Report', icon: 'bug', color: '#EF4444' },
    { id: 'feature', label: 'Feature Request', icon: 'bulb', color: '#3B82F6' },
    { id: 'improvement', label: 'Improvement', icon: 'trending-up', color: '#10B981' },
    { id: 'other', label: 'Other', icon: 'chatbubble', color: '#6B7280' },
  ];

  useEffect(() => {
    loadFeedbacks();
  }, []);

  const loadFeedbacks = async () => {
    try {
      const response = await api.get('/feedback');
      setFeedbacks(response.data.feedbacks || []);
    } catch (error) {
      console.error('Load feedbacks error:', error);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const onRefresh = () => {
    setRefreshing(true);
    loadFeedbacks();
  };

  const handleSubmit = async () => {
    if (!title.trim() || !description.trim()) {
      alert('Please fill in all fields');
      return;
    }

    setSubmitting(true);
    try {
      await api.post('/feedback', {
        category,
        title: title.trim(),
        description: description.trim(),
      });
      
      // Reset form
      setTitle('');
      setDescription('');
      setCategory('feature');
      setShowForm(false);
      
      // Reload feedbacks
      loadFeedbacks();
      alert('Feedback submitted successfully!');
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to submit feedback');
    } finally {
      setSubmitting(false);
    }
  };

  const handleUpvote = async (feedbackId: string) => {
    try {
      await api.post(`/feedback/${feedbackId}/upvote`);
      // Update local state
      setFeedbacks(feedbacks.map(f => 
        f.feedback_id === feedbackId 
          ? { ...f, upvotes: f.upvotes + (f.user_upvoted ? -1 : 1), user_upvoted: !f.user_upvoted }
          : f
      ));
    } catch (error: any) {
      console.error('Upvote error:', error);
    }
  };

  const getCategoryInfo = (categoryId: string) => {
    return categories.find(c => c.id === categoryId) || categories[3];
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'new': return '#3B82F6';
      case 'in_progress': return '#F59E0B';
      case 'completed': return '#10B981';
      case 'closed': return '#6B7280';
      default: return '#9CA3AF';
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        style={styles.keyboardView}
      >
        {/* Header */}
        <View style={styles.header}>
          <View>
            <Text style={styles.title}>Feedback Board</Text>
            <Text style={styles.subtitle}>Help us improve Carter</Text>
          </View>
          <TouchableOpacity
            style={styles.addButton}
            onPress={() => setShowForm(!showForm)}
          >
            <Ionicons name={showForm ? "close" : "add"} size={24} color="#FFF" />
          </TouchableOpacity>
        </View>

        {/* Submit Form */}
        {showForm && (
          <View style={styles.form}>
            <Text style={styles.formTitle}>Submit Feedback</Text>
            
            {/* Category Selection */}
            <View style={styles.categoryContainer}>
              {categories.map((cat) => (
                <TouchableOpacity
                  key={cat.id}
                  style={[
                    styles.categoryChip,
                    category === cat.id && { backgroundColor: cat.color, borderColor: cat.color },
                  ]}
                  onPress={() => setCategory(cat.id)}
                >
                  <Ionicons 
                    name={cat.icon as any} 
                    size={16} 
                    color={category === cat.id ? '#FFF' : cat.color} 
                  />
                  <Text
                    style={[
                      styles.categoryChipText,
                      category === cat.id && styles.categoryChipTextActive,
                    ]}
                  >
                    {cat.label}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <TextInput
              style={styles.input}
              placeholder="Title"
              value={title}
              onChangeText={setTitle}
              maxLength={100}
            />

            <TextInput
              style={[styles.input, styles.textArea]}
              placeholder="Description"
              value={description}
              onChangeText={setDescription}
              multiline
              numberOfLines={4}
              maxLength={500}
            />

            <TouchableOpacity
              style={[styles.submitButton, submitting && styles.submitButtonDisabled]}
              onPress={handleSubmit}
              disabled={submitting}
            >
              {submitting ? (
                <ActivityIndicator color="#FFF" />
              ) : (
                <>
                  <Ionicons name="send" size={20} color="#FFF" />
                  <Text style={styles.submitButtonText}>Submit Feedback</Text>
                </>
              )}
            </TouchableOpacity>
          </View>
        )}

        {/* Feedback List */}
        <ScrollView
          contentContainerStyle={styles.content}
          refreshControl={
            <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
          }
        >
          {feedbacks.length === 0 ? (
            <View style={styles.emptyState}>
              <Ionicons name="chatbubbles-outline" size={64} color="#D1D5DB" />
              <Text style={styles.emptyText}>No feedback yet</Text>
              <Text style={styles.emptySubtext}>Be the first to share your thoughts!</Text>
            </View>
          ) : (
            feedbacks.map((feedback) => {
              const categoryInfo = getCategoryInfo(feedback.category);
              return (
                <View key={feedback.feedback_id} style={styles.feedbackCard}>
                  <View style={styles.feedbackHeader}>
                    <View style={[styles.categoryBadge, { backgroundColor: `${categoryInfo.color}20` }]}>
                      <Ionicons name={categoryInfo.icon as any} size={14} color={categoryInfo.color} />
                      <Text style={[styles.categoryBadgeText, { color: categoryInfo.color }]}>
                        {categoryInfo.label}
                      </Text>
                    </View>
                    <View style={[styles.statusBadge, { backgroundColor: getStatusColor(feedback.status) }]}>
                      <Text style={styles.statusText}>{feedback.status.replace('_', ' ')}</Text>
                    </View>
                  </View>

                  <Text style={styles.feedbackTitle}>{feedback.title}</Text>
                  <Text style={styles.feedbackDescription} numberOfLines={3}>
                    {feedback.description}
                  </Text>

                  <View style={styles.feedbackFooter}>
                    <View style={styles.feedbackMeta}>
                      <Ionicons name="person-circle" size={16} color="#9CA3AF" />
                      <Text style={styles.feedbackUser}>{feedback.user_name}</Text>
                      <Text style={styles.feedbackDate}>
                        {new Date(feedback.created_at).toLocaleDateString()}
                      </Text>
                    </View>

                    <TouchableOpacity
                      style={[
                        styles.upvoteButton,
                        feedback.user_upvoted && styles.upvoteButtonActive,
                      ]}
                      onPress={() => handleUpvote(feedback.feedback_id)}
                    >
                      <Ionicons
                        name={feedback.user_upvoted ? "arrow-up" : "arrow-up-outline"}
                        size={18}
                        color={feedback.user_upvoted ? "#3B82F6" : "#6B7280"}
                      />
                      <Text
                        style={[
                          styles.upvoteText,
                          feedback.user_upvoted && styles.upvoteTextActive,
                        ]}
                      >
                        {feedback.upvotes}
                      </Text>
                    </TouchableOpacity>
                  </View>
                </View>
              );
            })
          )}
        </ScrollView>
      </KeyboardAvoidingView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  keyboardView: {
    flex: 1,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 16,
    paddingBottom: 12,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F2937',
  },
  subtitle: {
    fontSize: 14,
    color: '#6B7280',
    marginTop: 2,
  },
  addButton: {
    width: 48,
    height: 48,
    borderRadius: 24,
    backgroundColor: '#3B82F6',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 4,
    elevation: 4,
  },
  form: {
    backgroundColor: '#FFF',
    marginHorizontal: 16,
    marginBottom: 16,
    padding: 16,
    borderRadius: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  formTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 12,
  },
  categoryContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    marginBottom: 12,
  },
  categoryChip: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 20,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    backgroundColor: '#FFF',
  },
  categoryChipText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
  },
  categoryChipTextActive: {
    color: '#FFF',
  },
  input: {
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 12,
    fontSize: 16,
    color: '#1F2937',
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  textArea: {
    height: 100,
    textAlignVertical: 'top',
  },
  submitButton: {
    backgroundColor: '#3B82F6',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 12,
    borderRadius: 12,
    gap: 8,
  },
  submitButtonDisabled: {
    opacity: 0.5,
  },
  submitButtonText: {
    fontSize: 16,
    fontWeight: '700',
    color: '#FFF',
  },
  content: {
    paddingHorizontal: 16,
    paddingBottom: 24,
  },
  emptyState: {
    alignItems: 'center',
    paddingVertical: 80,
    paddingHorizontal: 32,
  },
  emptyText: {
    fontSize: 20,
    fontWeight: '600',
    color: '#6B7280',
    marginTop: 16,
    textAlign: 'center',
  },
  emptySubtext: {
    fontSize: 14,
    color: '#9CA3AF',
    marginTop: 8,
    textAlign: 'center',
  },
  feedbackCard: {
    backgroundColor: '#FFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  feedbackHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
  },
  categoryBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  categoryBadgeText: {
    fontSize: 12,
    fontWeight: '600',
  },
  statusBadge: {
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 12,
  },
  statusText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFF',
    textTransform: 'uppercase',
  },
  feedbackTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 8,
  },
  feedbackDescription: {
    fontSize: 14,
    color: '#6B7280',
    lineHeight: 20,
    marginBottom: 12,
  },
  feedbackFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
  },
  feedbackMeta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
  },
  feedbackUser: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
  },
  feedbackDate: {
    fontSize: 12,
    color: '#9CA3AF',
  },
  upvoteButton: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    backgroundColor: '#F3F4F6',
  },
  upvoteButtonActive: {
    backgroundColor: '#DBEAFE',
  },
  upvoteText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#6B7280',
  },
  upvoteTextActive: {
    color: '#3B82F6',
  },
});
