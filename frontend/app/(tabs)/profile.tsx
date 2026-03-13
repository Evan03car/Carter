import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  StyleSheet,
  ScrollView,
  TouchableOpacity,
  Image,
  ActivityIndicator,
} from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../../contexts/AuthContext';
import { router } from 'expo-router';
import api from '../../utils/api';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

export default function ProfileScreen() {
  const { user, logout } = useAuth();
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadDashboard();
  }, []);

  const loadDashboard = async () => {
    try {
      const response = await api.get('/dashboard');
      setDashboardData(response.data);
    } catch (error) {
      console.error('Dashboard error:', error);
    }
  };

  const handleUpgrade = async (plan: string) => {
    setLoading(true);
    try {
      const response = await api.post('/subscriptions/checkout', {
        type: 'subscription',
        plan: plan,
        origin_url: API_URL,
      });
      alert(`Opening payment page... URL: ${response.data.url}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  const handleBuySearches = async (pack: string) => {
    setLoading(true);
    try {
      const response = await api.post('/subscriptions/checkout', {
        type: 'search_pack',
        pack: pack,
        origin_url: API_URL,
      });
      alert(`Opening payment page... URL: ${response.data.url}`);
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Checkout failed');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    await logout();
    router.replace('/');
  };

  const tierColors: any = {
    free_trial: { bg: '#FEF3C7', text: '#92400E', label: 'Free Trial' },
    basic: { bg: '#DBEAFE', text: '#1E40AF', label: 'Basic Plan - 10/day' },
    premium: { bg: '#F3E8FF', text: '#6B21A8', label: 'Premium Plan - 300/day' },
  };

  const tierColor = tierColors[user?.subscription_tier || 'free_trial'];
  const userData = dashboardData?.user || user;
  const purchasedSearches = userData?.purchased_searches || 0;

  return (
    <SafeAreaView style={styles.container} edges={['top']}>
      <ScrollView contentContainerStyle={styles.content}>
        {/* Profile Header */}
        <View style={styles.profileHeader}>
          {user?.picture ? (
            <Image source={{ uri: user.picture }} style={styles.avatar} />
          ) : (
            <View style={[styles.avatar, styles.avatarPlaceholder]}>
              <Ionicons name="person" size={40} color="#9CA3AF" />
            </View>
          )}
          <Text style={styles.name}>{user?.name}</Text>
          <Text style={styles.email}>{user?.email}</Text>
          <View style={[styles.tierBadge, { backgroundColor: tierColor.bg }]}>
            <Text style={[styles.tierText, { color: tierColor.text }]}>
              {tierColor.label}
            </Text>
          </View>
          {purchasedSearches > 0 && (
            <View style={styles.searchesBadge}>
              <Ionicons name="flash" size={16} color="#F59E0B" />
              <Text style={styles.searchesText}>{purchasedSearches} bonus searches</Text>
            </View>
          )}
        </View>

        {/* Purchase Search Packs */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Buy Additional Searches</Text>
          <View style={styles.searchPacks}>
            <TouchableOpacity 
              style={styles.packCard}
              onPress={() => handleBuySearches('10')}
              disabled={loading}
            >
              <View style={styles.packHeader}>
                <Ionicons name="search" size={32} color="#3B82F6" />
                <View style={styles.packBadge}>
                  <Text style={styles.packBadgeText}>10 Searches</Text>
                </View>
              </View>
              <Text style={styles.packPrice}>$5</Text>
              <Text style={styles.packSubtext}>Never expires</Text>
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.packCard, styles.popularPack]}
              onPress={() => handleBuySearches('25')}
              disabled={loading}
            >
              <View style={styles.popularLabel}>
                <Text style={styles.popularLabelText}>BEST VALUE</Text>
              </View>
              <View style={styles.packHeader}>
                <Ionicons name="flash" size={32} color="#F59E0B" />
                <View style={[styles.packBadge, { backgroundColor: '#FEF3C7' }]}>
                  <Text style={[styles.packBadgeText, { color: '#92400E' }]}>25 Searches</Text>
                </View>
              </View>
              <Text style={styles.packPrice}>$7</Text>
              <Text style={styles.packSubtext}>Save $5 • Never expires</Text>
            </TouchableOpacity>
          </View>
        </View>

        {/* Upgrade Section */}
        {user?.subscription_tier !== 'premium' && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Subscription Plans</Text>
            
            <TouchableOpacity 
              style={styles.upgradeCard} 
              onPress={() => handleUpgrade('basic')}
              disabled={loading}
            >
              <View style={styles.upgradeContent}>
                <Ionicons name="briefcase" size={32} color="#3B82F6" />
                <View style={styles.upgradeText}>
                  <Text style={styles.upgradeTitle}>Basic Plan - $12/month</Text>
                  <Text style={styles.upgradeSubtitle}>
                    10 searches per day • Deal alerts
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#9CA3AF" />
            </TouchableOpacity>

            <TouchableOpacity 
              style={[styles.upgradeCard, styles.premiumCard]} 
              onPress={() => handleUpgrade('premium')}
              disabled={loading}
            >
              <View style={styles.upgradeContent}>
                <Ionicons name="rocket" size={32} color="#A855F7" />
                <View style={styles.upgradeText}>
                  <Text style={styles.upgradeTitle}>Premium Plan - $40/month</Text>
                  <Text style={styles.upgradeSubtitle}>
                    300 searches per day • Priority alerts • Advanced analytics
                  </Text>
                </View>
              </View>
              <Ionicons name="chevron-forward" size={24} color="#9CA3AF" />
            </TouchableOpacity>
          </View>
        )}

        {/* Menu Items */}
        <View style={styles.section}>
          <TouchableOpacity style={styles.menuItem}>
            <View style={styles.menuIcon}>
              <Ionicons name="notifications-outline" size={24} color="#3B82F6" />
            </View>
            <Text style={styles.menuText}>Deal Alerts</Text>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <View style={styles.menuIcon}>
              <Ionicons name="card-outline" size={24} color="#10B981" />
            </View>
            <Text style={styles.menuText}>Subscription</Text>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>

          <TouchableOpacity style={styles.menuItem}>
            <View style={styles.menuIcon}>
              <Ionicons name="settings-outline" size={24} color="#6B7280" />
            </View>
            <Text style={styles.menuText}>Settings</Text>
            <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
          </TouchableOpacity>
        </View>

        {/* Logout Button */}
        <TouchableOpacity style={styles.logoutButton} onPress={handleLogout}>
          <Ionicons name="log-out-outline" size={20} color="#EF4444" />
          <Text style={styles.logoutText}>Log Out</Text>
        </TouchableOpacity>

        <Text style={styles.version}>Version 1.0.0</Text>

        {loading && (
          <View style={styles.loadingOverlay}>
            <ActivityIndicator size="large" color="#3B82F6" />
          </View>
        )}
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB',
  },
  content: {
    paddingHorizontal: 16,
    paddingBottom: 32,
  },
  profileHeader: {
    alignItems: 'center',
    paddingVertical: 32,
  },
  avatar: {
    width: 80,
    height: 80,
    borderRadius: 40,
    marginBottom: 16,
  },
  avatarPlaceholder: {
    backgroundColor: '#E5E7EB',
    justifyContent: 'center',
    alignItems: 'center',
  },
  name: {
    fontSize: 24,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 4,
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12,
  },
  tierBadge: {
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 20,
  },
  tierText: {
    fontSize: 12,
    fontWeight: '700',
  },
  upgradeCard: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    backgroundColor: '#EFF6FF',
    padding: 20,
    borderRadius: 16,
    marginBottom: 24,
    borderWidth: 2,
    borderColor: '#3B82F6',
  },
  upgradeContent: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    gap: 16,
  },
  upgradeText: {
    flex: 1,
  },
  upgradeTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 4,
  },
  upgradeSubtitle: {
    fontSize: 12,
    color: '#6B7280',
  },
  section: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 4,
    elevation: 2,
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 16,
    paddingHorizontal: 16,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  menuIcon: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#F9FAFB',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12,
  },
  menuText: {
    flex: 1,
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
  },
  logoutButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#FFFFFF',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 24,
    gap: 8,
    borderWidth: 1,
    borderColor: '#FEE2E2',
  },
  logoutText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#EF4444',
  },
  version: {
    fontSize: 12,
    color: '#9CA3AF',
    textAlign: 'center',
    marginTop: 24,
  },
  searchesBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginTop: 8,
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: '#FEF3C7',
    borderRadius: 16,
  },
  searchesText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#92400E',
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 12,
  },
  searchPacks: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 16,
  },
  packCard: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 16,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#E5E7EB',
  },
  popularPack: {
    borderColor: '#F59E0B',
    position: 'relative',
  },
  popularLabel: {
    position: 'absolute',
    top: -8,
    backgroundColor: '#F59E0B',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  popularLabelText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#FFF',
  },
  packHeader: {
    alignItems: 'center',
    marginBottom: 8,
  },
  packBadge: {
    backgroundColor: '#DBEAFE',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
  },
  packBadgeText: {
    fontSize: 12,
    fontWeight: '700',
    color: '#1E40AF',
  },
  packPrice: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1F2937',
    marginBottom: 4,
  },
  packSubtext: {
    fontSize: 12,
    color: '#6B7280',
    textAlign: 'center',
  },
  premiumCard: {
    borderColor: '#A855F7',
    borderWidth: 2,
  },
  loadingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
  },
});