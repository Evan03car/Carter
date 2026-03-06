import React from 'react';
import { View, Text, StyleSheet, Image, TouchableOpacity, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { MarketplaceItem } from '../utils/api';

interface DealCardProps {
  item: MarketplaceItem;
  onSave?: () => void;
  onDelete?: () => void;
  showSaveButton?: boolean;
}

export default function DealCard({ item, onSave, onDelete, showSaveButton = true }: DealCardProps) {
  const openLink = () => {
    if (item.url) {
      Linking.openURL(item.url);
    }
  };

  const profitColor = (item.profit_margin || 0) >= 50 ? '#10B981' : (item.profit_margin || 0) >= 30 ? '#F59E0B' : '#3B82F6';

  return (
    <TouchableOpacity style={styles.card} onPress={openLink} activeOpacity={0.7}>
      <View style={styles.header}>
        <View style={styles.titleContainer}>
          <Text style={styles.title} numberOfLines={2}>{item.title}</Text>
          <View style={styles.platformBadge}>
            <Text style={styles.platformText}>{item.platform}</Text>
          </View>
        </View>
        {showSaveButton ? (
          <TouchableOpacity onPress={onSave} style={styles.iconButton}>
            <Ionicons name="bookmark-outline" size={24} color="#3B82F6" />
          </TouchableOpacity>
        ) : (
          <TouchableOpacity onPress={onDelete} style={styles.iconButton}>
            <Ionicons name="trash-outline" size={24} color="#EF4444" />
          </TouchableOpacity>
        )}
      </View>

      {item.image_url && (
        <Image source={{ uri: item.image_url }} style={styles.image} />
      )}

      <View style={styles.priceContainer}>
        <View>
          <Text style={styles.label}>Purchase Price</Text>
          <Text style={styles.price}>${item.price.toFixed(2)}</Text>
        </View>
        <Ionicons name="arrow-forward" size={20} color="#9CA3AF" />
        <View>
          <Text style={styles.label}>Est. Resale</Text>
          <Text style={styles.resalePrice}>${(item.estimated_resale_price || 0).toFixed(2)}</Text>
        </View>
      </View>

      <View style={styles.profitContainer}>
        <View style={[styles.profitBadge, { backgroundColor: profitColor }]}>
          <Ionicons name="trending-up" size={16} color="#FFF" />
          <Text style={styles.profitText}>{(item.profit_margin || 0).toFixed(1)}% Profit</Text>
        </View>
        <Text style={styles.netProfit}>
          ${((item.estimated_resale_price || 0) - item.price).toFixed(2)} net
        </Text>
      </View>

      {item.demand_level && (
        <View style={styles.footer}>
          <View style={styles.demandBadge}>
            <Ionicons name="flame" size={14} color="#EF4444" />
            <Text style={styles.demandText}>{item.demand_level.toUpperCase()} Demand</Text>
          </View>
          {item.best_resell_platform && (
            <Text style={styles.bestPlatform}>Best: {item.best_resell_platform}</Text>
          )}
        </View>
      )}

      {item.location && (
        <View style={styles.locationContainer}>
          <Ionicons name="location-outline" size={14} color="#6B7280" />
          <Text style={styles.locationText}>{item.location}</Text>
        </View>
      )}
    </TouchableOpacity>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 8,
    elevation: 3,
  },
  header: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    marginBottom: 12,
  },
  titleContainer: {
    flex: 1,
    marginRight: 8,
  },
  title: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4,
  },
  platformBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 6,
    alignSelf: 'flex-start',
  },
  platformText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#4F46E5',
  },
  iconButton: {
    padding: 4,
  },
  image: {
    width: '100%',
    height: 200,
    borderRadius: 12,
    marginBottom: 12,
    backgroundColor: '#F3F4F6',
  },
  priceContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 12,
    paddingVertical: 12,
    borderTopWidth: 1,
    borderBottomWidth: 1,
    borderColor: '#E5E7EB',
  },
  label: {
    fontSize: 12,
    color: '#6B7280',
    marginBottom: 4,
  },
  price: {
    fontSize: 20,
    fontWeight: '700',
    color: '#1F2937',
  },
  resalePrice: {
    fontSize: 20,
    fontWeight: '700',
    color: '#10B981',
  },
  profitContainer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  profitBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 12,
    paddingVertical: 6,
    borderRadius: 20,
    gap: 4,
  },
  profitText: {
    fontSize: 14,
    fontWeight: '700',
    color: '#FFF',
  },
  netProfit: {
    fontSize: 14,
    fontWeight: '600',
    color: '#10B981',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 8,
  },
  demandBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
  },
  demandText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#EF4444',
  },
  bestPlatform: {
    fontSize: 12,
    color: '#6B7280',
  },
  locationContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    marginTop: 8,
  },
  locationText: {
    fontSize: 12,
    color: '#6B7280',
  },
});