import * as ImagePicker from 'expo-image-picker';
import { useState } from 'react';
import {
  ActivityIndicator,
  Image,
  Platform,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
  View,
} from 'react-native';

const API_BASE_URL =
  Platform.OS === 'android' ? 'http://10.0.2.2:5000' : 'http://127.0.0.1:5000';

type Language = 'en' | 'ur';
type CropOption = 'tomato' | 'potato' | 'maize';

type PredictionResponse = {
  disease_name: string;
  crop_name: string;
  confidence: number;
  recommendation: {
    pesticide: string;
    dosage: string;
    treatment_steps: string[];
    prevention_tips: string[];
  };
  weather_risk?: {
    risk_level?: string;
    message?: string;
    temperature_c?: number;
    humidity_percent?: number;
  };
};

const textPack = {
  en: {
    title: 'Smart Crop Disease Detection',
    subtitle: 'Upload a leaf image for instant diagnosis and treatment recommendations.',
    language: 'Language',
    farmerId: 'Farmer ID',
    crop: 'Crop',
    latitude: 'Latitude (optional)',
    longitude: 'Longitude (optional)',
    chooseImage: 'Choose Leaf Image',
    analyze: 'Analyze Disease',
    pesticide: 'Recommended pesticide',
    dosage: 'Dosage',
    treatment: 'Treatment steps',
    prevention: 'Prevention tips',
    weatherRisk: 'Weather risk',
    noImage: 'Please select an image first.',
  },
  ur: {
    title: 'اسمارٹ کراپ ڈیزیز ڈٹیکشن',
    subtitle: 'فوری تشخیص اور علاج کے لئے پتے کی تصویر اپ لوڈ کریں۔',
    language: 'زبان',
    farmerId: 'کسان آئی ڈی',
    crop: 'فصل',
    latitude: 'عرض بلد (اختیاری)',
    longitude: 'طول بلد (اختیاری)',
    chooseImage: 'پتے کی تصویر منتخب کریں',
    analyze: 'بیماری معلوم کریں',
    pesticide: 'تجویز کردہ دوا',
    dosage: 'مقدار',
    treatment: 'علاج کے مراحل',
    prevention: 'بچاؤ کے طریقے',
    weatherRisk: 'موسمی خطرہ',
    noImage: 'پہلے تصویر منتخب کریں۔',
  },
};

export default function DetectionScreen() {
  const [lang, setLang] = useState<Language>('en');
  const [farmerId, setFarmerId] = useState('farmer-001');
  const [crop, setCrop] = useState<CropOption>('tomato');
  const [latitude, setLatitude] = useState('');
  const [longitude, setLongitude] = useState('');
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [result, setResult] = useState<PredictionResponse | null>(null);
  const [cachedResult, setCachedResult] = useState<PredictionResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const t = textPack[lang];

  const pickImage = async () => {
    setError('');
    const permission = await ImagePicker.requestMediaLibraryPermissionsAsync();
    if (!permission.granted) {
      setError('Media library permission is required.');
      return;
    }

    const picked = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ImagePicker.MediaTypeOptions.Images,
      quality: 0.9,
    });

    if (!picked.canceled && picked.assets.length > 0) {
      setImageUri(picked.assets[0].uri);
    }
  };

  const analyzeImage = async () => {
    if (!imageUri) {
      setError(t.noImage);
      return;
    }

    setLoading(true);
    setError('');
    setResult(null);

    try {
      const body = new FormData();
      body.append(
        'image',
        {
          uri: imageUri,
          name: 'leaf.jpg',
          type: 'image/jpeg',
        } as any,
      );
      body.append('farmer_id', farmerId);
      body.append('crop', crop);
      body.append('lang', lang);
      body.append('latitude', latitude);
      body.append('longitude', longitude);

      const response = await fetch(`${API_BASE_URL}/api/predict`, {
        method: 'POST',
        body,
      });

      const data = await response.json();
      if (!response.ok) {
        throw new Error(data.error || 'Prediction failed.');
      }

      setResult(data);
      setCachedResult(data);
    } catch (err: any) {
      if (cachedResult) {
        setResult(cachedResult);
        setError('Backend unavailable. Showing last cached result.');
      } else {
        setError(err.message || 'Unable to connect backend.');
      }
    } finally {
      setLoading(false);
    }
  };

  const resetSearch = () => {
    setLatitude('');
    setLongitude('');
    setImageUri(null);
    setResult(null);
    setError('');
  };

  return (
    <ScrollView style={styles.screen} contentContainerStyle={styles.content}>
      <Text style={styles.title}>{t.title}</Text>
      <Text style={styles.subtitle}>{t.subtitle}</Text>

      <View style={styles.langRow}>
        <Text style={styles.label}>{t.language}</Text>
        <View style={styles.langButtons}>
          <TouchableOpacity
            style={[styles.langButton, lang === 'en' && styles.langButtonActive]}
            onPress={() => setLang('en')}>
            <Text style={styles.langText}>EN</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={[styles.langButton, lang === 'ur' && styles.langButtonActive]}
            onPress={() => setLang('ur')}>
            <Text style={styles.langText}>UR</Text>
          </TouchableOpacity>
        </View>
      </View>

      <Text style={styles.label}>{t.farmerId}</Text>
      <TextInput style={styles.input} value={farmerId} onChangeText={setFarmerId} />

      <Text style={styles.label}>{t.crop}</Text>
      <View style={styles.cropRow}>
        {(['tomato', 'potato', 'maize'] as CropOption[]).map((option) => (
          <TouchableOpacity
            key={option}
            style={[styles.cropBtn, crop === option && styles.cropBtnActive]}
            onPress={() => setCrop(option)}>
            <Text style={[styles.cropBtnText, crop === option && styles.cropBtnTextActive]}>
              {option.charAt(0).toUpperCase() + option.slice(1)}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <Text style={styles.label}>{t.latitude}</Text>
      <TextInput style={styles.input} value={latitude} onChangeText={setLatitude} />

      <Text style={styles.label}>{t.longitude}</Text>
      <TextInput style={styles.input} value={longitude} onChangeText={setLongitude} />

      <TouchableOpacity style={styles.secondaryBtn} onPress={pickImage}>
        <Text style={styles.secondaryBtnText}>{t.chooseImage}</Text>
      </TouchableOpacity>

      {imageUri ? <Image source={{ uri: imageUri }} style={styles.preview} /> : null}

      <TouchableOpacity style={styles.primaryBtn} onPress={analyzeImage}>
        <Text style={styles.primaryBtnText}>{t.analyze}</Text>
      </TouchableOpacity>
      <TouchableOpacity style={styles.secondaryBtn} onPress={resetSearch}>
        <Text style={styles.secondaryBtnText}>Search Again</Text>
      </TouchableOpacity>

      {loading ? <ActivityIndicator size="large" color="#177245" style={{ marginTop: 12 }} /> : null}
      {error ? <Text style={styles.error}>{error}</Text> : null}

      {result ? (
        <View style={styles.resultCard}>
          <Text style={styles.resultTitle}>
            {result.disease_name} ({(result.confidence * 100).toFixed(2)}%)
          </Text>
          <Text style={styles.resultLine}>{result.crop_name}</Text>
          <Text style={styles.sectionTitle}>{t.pesticide}</Text>
          <Text style={styles.resultLine}>{result.recommendation.pesticide}</Text>
          <Text style={styles.sectionTitle}>{t.dosage}</Text>
          <Text style={styles.resultLine}>{result.recommendation.dosage}</Text>

          <Text style={styles.sectionTitle}>{t.treatment}</Text>
          {result.recommendation.treatment_steps.map((item) => (
            <Text style={styles.listItem} key={`t-${item}`}>
              - {item}
            </Text>
          ))}

          <Text style={styles.sectionTitle}>{t.prevention}</Text>
          {result.recommendation.prevention_tips.map((item) => (
            <Text style={styles.listItem} key={`p-${item}`}>
              - {item}
            </Text>
          ))}

          <Text style={styles.sectionTitle}>{t.weatherRisk}</Text>
          <Text style={styles.resultLine}>{result.weather_risk?.risk_level ?? 'unknown'}</Text>
        </View>
      ) : null}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  screen: {
    flex: 1,
    backgroundColor: '#f3f8f2',
  },
  content: {
    padding: 18,
    paddingBottom: 32,
  },
  title: {
    fontSize: 24,
    fontWeight: '700',
    color: '#15341e',
  },
  subtitle: {
    marginTop: 6,
    marginBottom: 16,
    color: '#446052',
  },
  langRow: {
    marginBottom: 10,
  },
  langButtons: {
    flexDirection: 'row',
    gap: 8,
    marginTop: 8,
  },
  langButton: {
    backgroundColor: '#e6f2e8',
    borderRadius: 8,
    paddingHorizontal: 14,
    paddingVertical: 8,
  },
  langButtonActive: {
    backgroundColor: '#bfe4c7',
  },
  langText: {
    fontWeight: '700',
    color: '#18482a',
  },
  label: {
    marginTop: 8,
    marginBottom: 6,
    color: '#204732',
    fontWeight: '600',
  },
  input: {
    backgroundColor: '#fff',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#d4e6d8',
    paddingHorizontal: 12,
    paddingVertical: 10,
  },
  cropRow: {
    flexDirection: 'row',
    gap: 8,
  },
  cropBtn: {
    flex: 1,
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#cbe2d0',
    backgroundColor: '#edf8ef',
    paddingVertical: 10,
    alignItems: 'center',
  },
  cropBtnActive: {
    backgroundColor: '#177245',
    borderColor: '#177245',
  },
  cropBtnText: {
    color: '#215438',
    fontWeight: '700',
  },
  cropBtnTextActive: {
    color: '#fff',
  },
  primaryBtn: {
    marginTop: 14,
    backgroundColor: '#177245',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  primaryBtnText: {
    color: '#fff',
    fontWeight: '700',
  },
  secondaryBtn: {
    marginTop: 12,
    backgroundColor: '#d9efe0',
    borderRadius: 10,
    paddingVertical: 12,
    alignItems: 'center',
  },
  secondaryBtnText: {
    color: '#18482a',
    fontWeight: '700',
  },
  preview: {
    width: '100%',
    height: 220,
    marginTop: 12,
    borderRadius: 12,
  },
  error: {
    marginTop: 10,
    color: '#af1f1f',
    fontWeight: '600',
  },
  resultCard: {
    marginTop: 16,
    backgroundColor: '#fff',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: '#d4e6d8',
    padding: 14,
  },
  resultTitle: {
    fontSize: 19,
    fontWeight: '700',
    color: '#173a23',
  },
  resultLine: {
    marginTop: 6,
    color: '#324d3f',
  },
  sectionTitle: {
    marginTop: 12,
    fontWeight: '700',
    color: '#173a23',
  },
  listItem: {
    marginTop: 4,
    color: '#324d3f',
  },
});
