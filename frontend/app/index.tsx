import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image, ActivityIndicator } from 'react-native';
import { router } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { LinearGradient } from 'expo-linear-gradient';

export default function Index() {
  const { user, loading } = useAuth();
  const [checking, setChecking] = useState(true);

  useEffect(() => {
    if (!loading) {
      if (user) {
        router.replace('/(tabs)');
      } else {
        setChecking(false);
      }
    }
  }, [user, loading]);

  if (checking || loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#3B82F6" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <LinearGradient
        colors={['#4F46E5', '#7C3AED', '#EC4899']}
        style={styles.gradient}
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
      />
      
      <View style={styles.content}>
        <View style={styles.logoContainer}>
          <Ionicons name="trending-up" size={80} color="#FFF" />
          <Text style={styles.logo}>Carter</Text>
          <Text style={styles.tagline}>Find Underpriced Items to Resell</Text>
        </View>

        <View style={styles.featuresContainer}>
          <View style={styles.feature}>
            <Ionicons name="search" size={32} color="#FFF" />
            <Text style={styles.featureText}>Scan Multiple Marketplaces</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="bulb" size={32} color="#FFF" />
            <Text style={styles.featureText}>AI Price Estimation</Text>
          </View>
          <View style={styles.feature}>
            <Ionicons name="notifications" size={32} color="#FFF" />
            <Text style={styles.featureText}>Deal Alerts</Text>
          </View>
        </View>

        <View style={styles.buttonContainer}>
          <TouchableOpacity
            style={styles.button}
            onPress={() => {
              // In real app, this would trigger OAuth flow
              // For now, go to login screen
              router.push('/auth-callback');
            }}
          >
            <Text style={styles.buttonText}>Get Started Free</Text>
            <Ionicons name="arrow-forward" size={20} color="#4F46E5" />
          </TouchableOpacity>
          <Text style={styles.trial}>7-day free trial • No credit card required</Text>
        </View>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  gradient: {
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    bottom: 0,
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
  },
  content: {
    flex: 1,
    paddingHorizontal: 24,
    paddingTop: 80,
    paddingBottom: 40,
  },
  logoContainer: {
    alignItems: 'center',
    marginBottom: 60,
  },
  logo: {
    fontSize: 40,
    fontWeight: '800',
    color: '#FFF',
    marginTop: 20,
  },
  tagline: {
    fontSize: 18,
    color: '#F3F4F6',
    marginTop: 8,
    textAlign: 'center',
  },
  featuresContainer: {
    gap: 24,
    marginBottom: 60,
  },
  feature: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 16,
    backgroundColor: 'rgba(255, 255, 255, 0.1)',
    padding: 20,
    borderRadius: 16,
  },
  featureText: {
    fontSize: 16,
    fontWeight: '600',
    color: '#FFF',
    flex: 1,
  },
  buttonContainer: {
    marginTop: 'auto',
  },
  button: {
    backgroundColor: '#FFF',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    paddingHorizontal: 32,
    borderRadius: 12,
    gap: 8,
  },
  buttonText: {
    fontSize: 18,
    fontWeight: '700',
    color: '#4F46E5',
  },
  trial: {
    fontSize: 14,
    color: '#F3F4F6',
    textAlign: 'center',
    marginTop: 16,
  },
});