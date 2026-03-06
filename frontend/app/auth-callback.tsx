import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { router, useLocalSearchParams } from 'expo-router';
import axios from 'axios';
import Constants from 'expo-constants';

const API_URL = Constants.expoConfig?.extra?.EXPO_PUBLIC_BACKEND_URL || process.env.EXPO_PUBLIC_BACKEND_URL;

export default function AuthCallback() {
  const { session_id } = useLocalSearchParams();
  const [error, setError] = useState('');

  useEffect(() => {
    if (session_id) {
      handleAuth(session_id as string);
    } else {
      // For demo, just redirect to tabs
      setTimeout(() => {
        router.replace('/(tabs)');
      }, 1000);
    }
  }, [session_id]);

  const handleAuth = async (sessionId: string) => {
    try {
      const response = await axios.post(
        `${API_URL}/api/auth/session`,
        {},
        {
          headers: {
            'X-Session-ID': sessionId,
          },
          withCredentials: true,
        }
      );

      if (response.status === 200) {
        router.replace('/(tabs)');
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Authentication failed');
      setTimeout(() => router.replace('/'), 2000);
    }
  };

  return (
    <View style={styles.container}>
      {error ? (
        <Text style={styles.error}>{error}</Text>
      ) : (
        <>
          <ActivityIndicator size="large" color="#3B82F6" />
          <Text style={styles.text}>Signing you in...</Text>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    paddingHorizontal: 24,
  },
  text: {
    fontSize: 16,
    color: '#6B7280',
    marginTop: 16,
  },
  error: {
    fontSize: 16,
    color: '#EF4444',
    textAlign: 'center',
  },
});