import React, { useEffect, useState } from 'react';
import { View, ActivityIndicator, StyleSheet } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import AsyncStorage from '@react-native-async-storage/async-storage';

export default function Index() {
  const { user, loading } = useAuth();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    checkOnboarding();
  }, [user, loading]);

  const checkOnboarding = async () => {
    if (loading) return;

    try {
      const hasSeenOnboarding = await AsyncStorage.getItem('hasSeenOnboarding');
      
      if (!hasSeenOnboarding) {
        // First time user - show onboarding
        router.replace('/onboarding');
      } else if (user) {
        // Returning user with auth - go to app
        router.replace('/(tabs)');
      } else {
        // Returning user without auth - stay on landing
        setChecking(false);
      }
    } catch (error) {
      console.error('Onboarding check error:', error);
      setChecking(false);
    }
  };

  if (checking || loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  // This landing page only shows for returning users who aren't logged in
  return null;
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
});