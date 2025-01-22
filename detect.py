import tensorflow as tf
from tensorflow.keras.layers import Dense, Flatten, Conv2D, GlobalAveragePooling2D, Input, Reshape, Multiply
from tensorflow.keras.models import Model, Sequential
from tensorflow.keras.optimizers import Adam
import numpy as np

# 1. Channel-Wise Attention Mechanism
def channel_attention(input_feature, ratio=8):
    channel = input_feature.shape[-1]
    shared_layer_one = Dense(channel // ratio, activation='relu')
    shared_layer_two = Dense(channel, activation='sigmoid')

    avg_pool = tf.reduce_mean(input_feature, axis=(1, 2), keepdims=True)
    avg_out = shared_layer_two(shared_layer_one(avg_pool))

    max_pool = tf.reduce_max(input_feature, axis=(1, 2), keepdims=True)
    max_out = shared_layer_two(shared_layer_one(max_pool))

    out = avg_out + max_out
    return Multiply()([input_feature, out])

# 2. ResNet50 with Channel-Wise Attention
def build_resnet_with_attention(input_shape=(224, 224, 3)):
    base_model = tf.keras.applications.ResNet50(include_top=False, weights='imagenet', input_shape=input_shape)
    x = base_model.output
    x = channel_attention(x)
    x = GlobalAveragePooling2D()(x)
    features = Dense(128, activation='relu')(x)  # Feature layer
    model = Model(inputs=base_model.input, outputs=features)
    return model

# 3. GAN Implementation
def build_gan(input_dim=128):
    # Generator
    generator = Sequential([
        Dense(256, activation='relu', input_dim=input_dim),
        Dense(512, activation='relu'),
        Dense(224 * 224 * 3, activation='tanh'),
        Reshape((224, 224, 3))
    ])

    # Discriminator
    discriminator = Sequential([
        Input(shape=(224, 224, 3)),
        Conv2D(64, kernel_size=3, strides=2, padding="same", activation='relu'),
        Conv2D(128, kernel_size=3, strides=2, padding="same", activation='relu'),
        Flatten(),
        Dense(1, activation='sigmoid')
    ])
    discriminator.compile(optimizer=Adam(learning_rate=0.0002), loss='binary_crossentropy', metrics=['accuracy'])

    return generator, discriminator

# 4. Hybrid Model
def build_hybrid_model(resnet_model, gan_discriminator):
    resnet_model.trainable = False  # Freeze ResNet layers
    input_img = Input(shape=(224, 224, 3))
    resnet_features = resnet_model(input_img)
    gan_output = gan_discriminator(input_img)
    combined_output = Dense(1, activation='sigmoid')(resnet_features)
    hybrid_output = Multiply()([combined_output, gan_output])
    hybrid_model = Model(inputs=input_img, outputs=hybrid_output)
    hybrid_model.compile(optimizer=Adam(learning_rate=0.0002), loss='binary_crossentropy', metrics=['accuracy'])
    return hybrid_model

# 5. Training and Evaluation
if __name__ == "__main__":
    # Build models
    resnet_model = build_resnet_with_attention()
    generator, discriminator = build_gan()
    hybrid_model = build_hybrid_model(resnet_model, discriminator)

    # Load dataset (replace with your dataset)
    (x_train, y_train), (x_test, y_test) = tf.keras.datasets.cifar10.load_data()
    x_train = tf.image.resize(x_train / 255.0, (224, 224))
    y_train = np.random.choice([0, 1], size=(len(y_train),))  # Dummy labels for demonstration

    # Train discriminator
    discriminator.fit(x_train, y_train, epochs=10, batch_size=32)

    # Train hybrid model
    hybrid_model.fit(x_train, y_train, validation_split=0.2, epochs=10, batch_size=32)

    # Evaluate model
    accuracy = hybrid_model.evaluate(x_test, y_test)
    print(f"Hybrid Model Accuracy: {accuracy[1]}")
