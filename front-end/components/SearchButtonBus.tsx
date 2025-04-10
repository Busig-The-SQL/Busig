import React from 'react';
import {StyleSheet, Text, TouchableOpacity, View} from 'react-native';
import {router} from 'expo-router';
import colors from '@/config/Colors';
import fonts from '@/config/Fonts';
import {Bus} from "@/types/bus";

const SearchButtonBus = ({ item } : {item : Bus}) => {
    return (
        <View style={styles.buttonContainer}>
            <TouchableOpacity
                style={styles.buttonContainer}
                // onPress={() => router.push({ pathname: `/screens/trip/${item.id}`, params: { bus: item.id } })}
                onPress={() => router.push(`/screens/trip/${item.id}`)}
                activeOpacity={0.1}
            >
                <View>
                    <Text style={styles.textPrimary}>
                        {`Bus ${item.route}`}  
                    </Text>
                    <Text style={styles.textSecondary}>
                        {`${item.headsign}`}  
                    </Text>
                </View>
            </TouchableOpacity>
        </View>
    );
};

const styles = StyleSheet.create({
    buttonContainer: {
        backgroundColor: colors.backgroundPrimary,
        padding: 5,
        paddingHorizontal: 7,
    },
    textPrimary: {
        fontSize: fonts.subHeading,
        color: colors.textPrimary,
    },
    textSecondary: {
        fontSize: fonts.body,
        color: colors.textSecondary,
    },
});

export default SearchButtonBus;