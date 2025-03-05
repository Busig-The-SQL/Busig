import React from 'react';
import {StyleSheet, Text, TouchableOpacity, View} from 'react-native';
import {router} from 'expo-router';

import colors from '@/config/Colors';
import fonts from '@/config/Fonts';
import {Route} from "@/types/route";

const SearchButtonRoute = ({ item }: { item: Route }) => {
    return (
        <View style={styles.buttonContainer}>
            <TouchableOpacity
                style={styles.buttonContainer}
                onPress={() => router.push({ pathname: `/screens/map/${item.name}`, params: { route: item.name } })}
                activeOpacity={0.1}
            >
                <View>
                    <Text style={styles.textPrimary}>
                        {`${item.name}`}  
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

export default SearchButtonRoute;