import tensorflow as tf
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Conv2D, MaxPooling2D, UpSampling2D, BatchNormalization

def build_autoencoder(input_shape=(224, 224, 1)):
    """
    Build Convolutional Autoencoder for Anomaly Detection
    """
    # Encoder
    input_img = Input(shape=input_shape)
    
    # Block 1
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(input_img)
    x = BatchNormalization()(x)
    x = MaxPooling2D((2, 2), padding='same')(x) # 112x112
    
    # Block 2
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = MaxPooling2D((2, 2), padding='same')(x) # 56x56
    
    # Block 3 (Latent Space Representation)
    x = Conv2D(128, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    encoded = MaxPooling2D((2, 2), padding='same')(x) # 28x28
    
    # Decoder
    
    # Block 3 Upsample
    x = Conv2D(128, (3, 3), activation='relu', padding='same')(encoded)
    x = BatchNormalization()(x)
    x = UpSampling2D((2, 2))(x) # 56x56
    
    # Block 2 Upsample
    x = Conv2D(64, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = UpSampling2D((2, 2))(x) # 112x112
    
    # Block 1 Upsample
    x = Conv2D(32, (3, 3), activation='relu', padding='same')(x)
    x = BatchNormalization()(x)
    x = UpSampling2D((2, 2))(x) # 224x224
    
    # Output Layer
    decoded = Conv2D(1, (3, 3), activation='sigmoid', padding='same')(x)
    
    # Model
    autoencoder = Model(input_img, decoded)
    
    # Compile
    # MSE is good for pixel-level reconstruction error (Difference Image)
    autoencoder.compile(optimizer='adam', loss='mean_squared_error')
    
    return autoencoder

if __name__ == "__main__":
    model = build_autoencoder()
    model.summary()
