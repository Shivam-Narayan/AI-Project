import streamlit as st
import py3Dmol
from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, RWMol, Draw
import matplotlib.pyplot as plt
from io import BytesIO
from deepchem.feat import ConvMolFeaturizer
import streamlit.components.v1 as components
from sklearn.metrics import mean_squared_error
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
import re
import random
from collections import deque
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.preprocessing import LabelEncoder
from rdkit import Chem
from rdkit.Chem import Descriptors, DataStructs
import tensorflow as tf
import plotly.express as px
import re
from langchain.document_loaders import TextLoader
from pypdf import PdfReader
from langchain import HuggingFaceHub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains import RetrievalQA
import pandas as pd
from docx import Document
import json
import lightgbm as lgb
import plotly.express as px
from datetime import datetime, timedelta
import plotly.graph_objects as go
import insurance_claim_mgmt as insurance_claim_mgmt
import Personalized_Medication_Recommendation as Personalized_Medication_Recommendation



# Define your first function
def script1():
    # Create a molecule from SMILES
    smiles = 'CC(=O)NC1=CC=C(C=C1)O'
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)

    # Generate 3D coordinates
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.UFFOptimizeMolecule(mol)

    # Convert to 3Dmol.js format
    mol_block = Chem.MolToMolBlock(mol)

    # Visualize with py3Dmol
    viewer = py3Dmol.view(width=300, height=200)
    viewer.addModel(mol_block, 'mol')
    viewer.setStyle({'stick': {}})
    viewer.setBackgroundColor('white')
    viewer.zoomTo()

    # Get the HTML and JS content
    return viewer

# Define your second function
def script2():
    # Define a molecule using SMILES
    smiles = 'CC(=O)NC1=CC=C(C=C1)O'  # Paracetamol
    mol = Chem.MolFromSmiles(smiles)

    # Calculate molecular weight
    mol_weight = Descriptors.MolWt(mol)

    # Calculate LogP
    logp = Descriptors.MolLogP(mol)

    # Calculate Topological Polar Surface Area (TPSA)
    tpsa = Descriptors.TPSA(mol)

    # Calculate number of hydrogen bond donors
    hbd = Descriptors.NumHDonors(mol)

    # Calculate number of hydrogen bond acceptors
    hba = Descriptors.NumHAcceptors(mol)

    # Calculate number of rotatable bonds
    rotatable_bonds = Descriptors.NumRotatableBonds(mol)

    # Generate a text block with the calculated properties
    text = f"""
    **Molecular Properties of {smiles}:**

    - Molecular Weight: {mol_weight:.2f}
    - LogP: {logp:.2f}
    - Topological Polar Surface Area (TPSA): {tpsa:.2f}
    - Number of Hydrogen Bond Donors: {hbd}
    - Number of Hydrogen Bond Acceptors: {hba}
    - Number of Rotatable Bonds: {rotatable_bonds}
    """
    return text

# Define your third function
def script3():
    # Original paracetamol molecule
    smiles = 'CC(=O)NC1=CC=C(C=C1)O'
    mol = Chem.MolFromSmiles(smiles)

    # Function to generate variants by modifying substituents
    def generate_variants(mol, num_variants=10):
        variants = []
        for _ in range(num_variants):
            rw_mol = RWMol(mol)
            # Randomly change a hydrogen to a methyl group as an example modification
            idx = rw_mol.GetNumAtoms() - 1  # Last atom index
            rw_mol.ReplaceAtom(idx, Chem.Atom('C'))
            variant = rw_mol.GetMol()
            Chem.SanitizeMol(variant)
            variants.append(variant)
        return variants

    variants = generate_variants(mol)
    variant_smiles = [Chem.MolToSmiles(variant) for variant in variants]
    print("Generated Variants SMILES:", variant_smiles)

    # Calculate molecular descriptors for each variant
    descriptors = []
    for variant in variants:
        desc = [Descriptors.MolWt(variant), Descriptors.NumRotatableBonds(variant)]
        descriptors.append(desc)

    # Format descriptors for display
    descriptors_text = "\n".join([f"Variant {i+1}: Molecular Weight: {d[0]:.2f}, Rotatable Bonds: {d[1]}" for i, d in enumerate(descriptors)])
    
    return variant_smiles

# Define your fourth function
def script4():
    # SMILES string for Paracetamol
    variant_smiles = "CC(=O)Nc1ccc(C)cc1"

    # Convert SMILES to molecule
    mol = Chem.MolFromSmiles(variant_smiles)

    # Draw the molecule
    img = Draw.MolToImage(mol, size=(300, 300))

    # Convert image to bytes
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()

    # Featurize the molecule using DeepChem
    featurizer = ConvMolFeaturizer()
    X_pred = featurizer.featurize([variant_smiles])

    # Check if featurization was successful
    if X_pred is None or len(X_pred) == 0 or X_pred[0] is None:
        text = "Featurization failed for the variant molecule."
    else:
        text = "Featurization successful."
    
    return byte_im, text

# Define your fifth function
def script5():

    # Create a molecule from SMILES
    smiles = 'CC(=O)Nc1ccc(C)cc1'
    mol = Chem.MolFromSmiles(smiles)
    mol = Chem.AddHs(mol)

    # Generate 3D coordinates
    AllChem.EmbedMolecule(mol, randomSeed=42)
    AllChem.UFFOptimizeMolecule(mol)

    # Convert to 3Dmol.js format
    mol_block = Chem.MolToMolBlock(mol)

    # Visualize with py3Dmol
    viewer = py3Dmol.view(width=300, height=200)
    viewer.addModel(mol_block, 'mol')
    viewer.setStyle({'stick': {}})
    viewer.setBackgroundColor('white')
    viewer.zoomTo()

    return viewer

def script6():
    # dummy dataset for Paracetamol
    data = {
        "Compound": ["Paracetamol_Variant_1", "Paracetamol_Variant_2", "Paracetamol_Variant_3", "Paracetamol_Variant_4"],
        "IC50 (µM)": [1.0, 0.75, 1.25, 0.5],
        "EC50 (µM)": [2.0, 1.5, 2.5, 1.0],
        "Ki (nM)": [15, 10, 20, 5],
        "Cell Viability (%)": [85, 90, 80, 95],
        "Comments": ["Moderate potency", "High potency", "Low potency", "Very high potency"]
    }

    paracetamol_activity_df = pd.DataFrame(data)

    # add SMILES for each variant
    paracetamol_activity_df['smiles'] = ["CC(=O)Nc1ccc(C)cc1"] * len(paracetamol_activity_df)  # Simplified example

    # Saving the DataFrame to a CSV file
    paracetamol_activity_df.to_csv('../templates/paracetamol_activity_data.csv', index=False)

    # Load the synthetic dataset
    data = pd.read_csv('../templates/paracetamol_activity_data.csv')

    # Function to featurize molecules using RDKit
    def featurize(smiles):
        molecule = Chem.MolFromSmiles(smiles)
        if molecule is None:
            return None
        features = np.array([
            Descriptors.MolWt(molecule),
            Descriptors.MolLogP(molecule),
            Descriptors.NumHDonors(molecule),
            Descriptors.NumHAcceptors(molecule)
        ])
        return features

    # Featurize
    data['features'] = data['smiles'].apply(featurize)
    data = data.dropna(subset=['features'])

    # Prepare the feature matrix
    X = np.stack(data['features'].values)

    # Extract target values
    y_ic50 = data['IC50 (µM)'].values
    y_ec50 = data['EC50 (µM)'].values
    y_ki = data['Ki (nM)'].values
    y_cv = data['Cell Viability (%)'].values

    # Split the data into training and test sets for each target
    X_train_ic50, X_test_ic50, y_train_ic50, y_test_ic50 = train_test_split(X, y_ic50, test_size=0.2, random_state=42)
    X_train_ec50, X_test_ec50, y_train_ec50, y_test_ec50 = train_test_split(X, y_ec50, test_size=0.2, random_state=42)
    X_train_ki, X_test_ki, y_train_ki, y_test_ki = train_test_split(X, y_ki, test_size=0.2, random_state=42)
    X_train_cv, X_test_cv, y_train_cv, y_test_cv = train_test_split(X, y_cv, test_size=0.2, random_state=42)

    # Train the Random Forest models
    model_ic50 = RandomForestRegressor(n_estimators=100, random_state=42)
    model_ec50 = RandomForestRegressor(n_estimators=100, random_state=42)
    model_ki = RandomForestRegressor(n_estimators=100, random_state=42)
    model_cv = RandomForestRegressor(n_estimators=100, random_state=42)

    model_ic50.fit(X_train_ic50, y_train_ic50)
    model_ec50.fit(X_train_ec50, y_train_ec50)
    model_ki.fit(X_train_ki, y_train_ki)
    model_cv.fit(X_train_cv, y_train_cv)

    # Evaluate the models
    y_pred_ic50 = model_ic50.predict(X_test_ic50)
    y_pred_ec50 = model_ec50.predict(X_test_ec50)
    y_pred_ki = model_ki.predict(X_test_ki)
    y_pred_cv = model_cv.predict(X_test_cv)

    mse_ic50 = mean_squared_error(y_test_ic50, y_pred_ic50)
    mse_ec50 = mean_squared_error(y_test_ec50, y_pred_ec50)
    mse_ki = mean_squared_error(y_test_ki, y_pred_ki)
    mse_cv = mean_squared_error(y_test_cv, y_pred_cv)


    text1 = f"""
    * Mean Squared Error for IC50: {mse_ic50:.2f}
    * Mean Squared Error for EC50: {mse_ec50:.2f}
    * Mean Squared Error for IC50: {mse_ki:.2f}
    * Mean Squared Error for Cell Viability: {mse_cv:.2f}
    """

    # SMILES string for Paracetamol variant
    target_smiles = "CC(=O)Nc1ccc(C)cc1"

    # Featurize the target molecule
    target_features = featurize(target_smiles)

    # Predict the activities for the target molecule
    if target_features is not None:
        target_features = target_features.reshape(1, -1)  # Reshape to match the model's input

        predicted_ic50 = model_ic50.predict(target_features)
        predicted_ec50 = model_ec50.predict(target_features)
        predicted_ki = model_ki.predict(target_features)
        predicted_cv = model_cv.predict(target_features)

        text2 = f"""
            * Predicted IC50 (µM) for Paracetamol: {predicted_ic50[0]:.2f}
            * Predicted EC50 (µM) for Paracetamol: {predicted_ec50[0]:.2f}
            * Predicted Ki (nM) for Paracetamol: {predicted_ki[0]:.2f}**
            * Predicted Cell Viability for Paracetamol: {predicted_cv[0]:.2f}%
            """
    else:
        print("Failed to featurize the target molecule.")
        text2 = "Failed to featurize the target molecule."

    return text1, text2

def script7():
    class DRLAgent:
        """
        Deep Reinforcement Learning Agent

        Args:
            state_size (int): Size of the state space
            action_size (int): Size of the action space
        """

        def __init__(self, state_size, action_size, selected_X_train):
            self.state_size = state_size
            self.action_size = action_size
            self.memory = deque(maxlen=2000)
            # discount rate
            self.gamma = 0.95
            # exploration rate
            self.epsilon = 1.0
            self.epsilon_min = 0.01
            self.epsilon_decay = 0.995
            self.learning_rate = 0.001
            self.selected_X_train = selected_X_train
            self.model = self._build_model(selected_X_train)
            # target model for stability
            self.target_model = self._build_model(selected_X_train) 
            self.update_target_model()

        def _build_model(self, selected_X_train):
            """
            Build the Deep Q-Network model

            Returns:
                model (Sequential): Deep Q-Network model
            """
            model = tf.keras.models.Sequential()
            model.add(tf.keras.layers.Dense(32, input_shape=(selected_X_train.shape[1],), activation='relu'))
            model.add(tf.keras.layers.Dense(16, activation='relu'))
            model.add(tf.keras.layers.Dense(self.action_size, activation='linear'))
            model.compile(loss='mse', optimizer=tf.keras.optimizers.Adam(learning_rate=self.learning_rate))
            return model

        def update_target_model(self):
            """Update the target model weights with the current model weights"""
            self.target_model.set_weights(self.model.get_weights())

        def remember(self, state, action, reward, next_state, done):
            """
            Store the experience in the replay memory

            Args:
                state (ndarray): Current state
                action (int): Action taken
                reward (float): Reward received
                next_state (ndarray): Next state
                done (bool): Whether the episode is done
            """
            self.memory.append((state, action, reward, next_state, done))

        def act(self, state):
            """
            Choose an action given the current state

            Args:
                state (ndarray): Current state

            Returns:
                action (int): Chosen action
            """
            if np.random.rand() <= self.epsilon:
                return np.random.randint(self.action_size)
            if state is None:
                state = np.zeros((1, self.state_size))
            else:
                state = state.reshape(1, self.state_size)
            act_values = self.model.predict(state)
            return np.argmax(act_values[0])

        def replay(self, batch_size):
            """
            Train the model by replaying experiences from the replay memory

            Args:
                batch_size (int): Size of the minibatch
            """
            # Sample a minibatch of experiences from the replay memory
            minibatch = random.sample(self.memory, batch_size)
            for state, action, reward, next_state, done in minibatch:
                if state is not None:
                    if not done:
                        # Calculate the target value using the target model
                        target = (reward + self.gamma * np.amax(self.target_model.predict(next_state)[0]))
                    else:
                        target = reward
                    # Make the agent approximately map the current state to future discounted reward
                    target_f = self.model.predict(state)
                    target_f[0][action] = target
                    # Train the model using the current state and target value
                    self.model.fit(state, target_f, epochs=1, verbose=0)
            # Decay the exploration rate
            if self.epsilon > self.epsilon_min:
                self.epsilon *= self.epsilon_decay

        def load(self, name):
            """Load the model weights from a file"""
            self.model.load_weights(name)

        def save(self, name):
            """Save the model weights to a file"""
            self.model.save_weights(name)


    def preprocess_smiles(smiles):
        """
        Preprocess the SMILES string by removing salts and stereochemistry information

        Args:
            smiles (str): SMILES string

        Returns:
            preprocessed_smiles (str): Preprocessed SMILES string
        """
        # Remove salts
        preprocessed_smiles = re.sub(r'\[.*?\]', '', smiles)
        # Remove stereochemistry information
        preprocessed_smiles = re.sub(r'[@]\S*', '', preprocessed_smiles)
        return preprocessed_smiles


    def calculate_molecular_properties(smiles):
        """
        Calculate molecular properties of a compound given its SMILES string

        Args:
            smiles (str): SMILES string

        Returns:
            properties (dict): Dictionary of molecular properties
        """
        molecule = Chem.MolFromSmiles(smiles)
        properties = {}

        if molecule is not None:
            properties['Molecular Weight'] = Descriptors.MolWt(molecule)
            properties['LogP'] = Descriptors.MolLogP(molecule)
            properties['H-Bond Donor Count'] = Descriptors.NumHDonors(molecule)
            properties['H-Bond Acceptor Count'] = Descriptors.NumHAcceptors(molecule)

        return properties


    
    smiles = 'CC(=O)NC1=CC=C(C=C1)O'
    preprocessed_smiles = preprocess_smiles(smiles)
    properties = calculate_molecular_properties(preprocessed_smiles)
    print(properties) # {'Molecular Weight': 180.15899999999996, 'LogP': 1.3101, 'H-Bond Donor Count': 1, 'H-Bond Acceptor Count': 3}
    
    # Convert the properties dictionary to a NumPy array
    selected_X_train = np.array(list(properties.values())).reshape(1, -1)

    agent = DRLAgent(state_size=selected_X_train.shape[1], action_size=3, selected_X_train=selected_X_train)

    # Get the model's output for the selected input
    output = agent.model.predict(selected_X_train)
    print("Model Output:", output)

    # Obtain the SMILES representation of the molecule after processing with the model
    reconstructed_smiles = Chem.MolToSmiles(Chem.MolFromSmiles(preprocessed_smiles))
    print("Reconstructed SMILES:", reconstructed_smiles)
    
    mol = Chem.MolFromSmiles(reconstructed_smiles)
    img = Draw.MolToImage(mol, size=(300, 300))
    # Convert image to bytes
    buf = BytesIO()
    img.save(buf, format="PNG")
    byte_im = buf.getvalue()
    if mol is None:
        print(f"Error generating molecule from SMILES: {reconstructed_smiles}")

    # Create a molecule from SMILES
    mol7_3d = Chem.MolFromSmiles(reconstructed_smiles)
    mol7_3d = Chem.AddHs(mol7_3d)

    # Generate 3D coordinates
    AllChem.EmbedMolecule(mol7_3d, randomSeed=42)
    AllChem.UFFOptimizeMolecule(mol7_3d)

    # Convert to 3Dmol.js format
    mol7_3d = Chem.MolToMolBlock(mol7_3d)

    # Visualize with py3Dmol
    viewer = py3Dmol.view(width=300, height=200)
    viewer.addModel(mol7_3d, 'mol')
    viewer.setStyle({'stick': {}})
    viewer.setBackgroundColor('white')
    viewer.zoomTo()

    # Get the HTML and JS content
    return output, reconstructed_smiles, properties, byte_im, viewer
   


def script8():
    # Parameters
    num_patients = 100  # Number of patients

    # Data generation
    np.random.seed(42)
    data = {
        'Patient_ID': range(1, num_patients + 1),
        'Age': np.random.randint(18, 66, num_patients),
        'Gender': np.random.choice(['Male', 'Female'], num_patients),
        'Weight_kg': np.random.randint(50, 101, num_patients),
        'Dose_mg': np.random.choice([500, 1000], num_patients),
        'Pain_Level_Before': np.random.randint(0, 11, num_patients),
        'Pain_Level_After': [max(0, x - np.random.randint(0, 6)) for x in np.random.randint(0, 11, num_patients)],
        'Side_Effects': np.random.choice(['None', 'Nausea', 'Dizziness'], num_patients),
        'Outcome': np.random.choice(['Improved', 'No Change', 'Worse'], num_patients),
        'Paracetamol_Variant': np.random.choice(['Paracetamol_Variant 1', 'Paracetamol_Variant 2', 'Paracetamol_Variant 3', 'Paracetamol_Variant 4'], num_patients)
    }

    # Creating DataFrame
    df = pd.DataFrame(data)

    # Adjusting Outcome based on Pain Levels
    df['Outcome'] = np.where(df['Pain_Level_Before'] > df['Pain_Level_After'], 'Improved', df['Outcome'])
    df['Outcome'] = np.where(df['Pain_Level_Before'] == df['Pain_Level_After'], 'No Change', df['Outcome'])
    df['Outcome'] = np.where(df['Pain_Level_Before'] < df['Pain_Level_After'], 'Worse', df['Outcome'])

    # Displaying the DataFrame in tabular format
    print(df.head(10).to_string(index=False))

def script9():
    # Parameters
    num_patients = 100  # Number of patients

    # Data generation
    np.random.seed(42)
    data = {
        'Patient_ID': range(1, num_patients + 1),
        'Age': np.random.randint(18, 66, num_patients),
        'Gender': np.random.choice(['Male', 'Female'], num_patients),
        'Weight_kg': np.random.randint(50, 101, num_patients),
        'Dose_mg': np.random.choice([500, 1000], num_patients),
        'Pain_Level_Before': np.random.randint(0, 11, num_patients),
        'Pain_Level_After': [max(0, x - np.random.randint(0, 6)) for x in np.random.randint(0, 11, num_patients)],
        'Side_Effects': np.random.choice(['None', 'Nausea', 'Dizziness'], num_patients),
        'Outcome': np.random.choice(['Improved', 'No Change', 'Worse'], num_patients),
        'Paracetamol_Variant': np.random.choice(['Paracetamol_Variant 1', 'Paracetamol_Variant 2', 'Paracetamol_Variant 3', 'Paracetamol_Variant 4'], num_patients)
    }

    # Creating DataFrame
    df = pd.DataFrame(data)

    # Adjusting Outcome based on Pain Levels
    df['Outcome'] = np.where(df['Pain_Level_Before'] > df['Pain_Level_After'], 'Improved', df['Outcome'])
    df['Outcome'] = np.where(df['Pain_Level_Before'] == df['Pain_Level_After'], 'No Change', df['Outcome'])
    df['Outcome'] = np.where(df['Pain_Level_Before'] < df['Pain_Level_After'], 'Worse', df['Outcome'])

    # Creating an interactive bar chart
    fig1 = px.bar(
        df, 
        x='Paracetamol_Variant', 
        color='Outcome',
        barmode='group',
        facet_col='Gender',
        category_orders={'Outcome': ['Improved', 'No Change', 'Worse']},
        title="Gender-wise Outcomes for Different Paracetamol Variants",
        labels={'Paracetamol_Variant': 'Paracetamol Variant', 'count': 'Number of Patients'}
    )


    # Adding Age Category
    bins = [18, 30, 40, 50, 65, 100]  # Adjusted to include ages up to 100
    labels = ['18-29', '30-39', '40-49', '50-65', '65+']
    df['Age_Category'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)

    # Optional: Remove rows with NaN in 'Age_Category' if any
    df = df.dropna(subset=['Age_Category'])

    # Creating an interactive bar chart
    fig2 = px.bar(
        df, 
        x='Paracetamol_Variant', 
        color='Outcome',
        barmode='group',
        facet_col='Age_Category',
        category_orders={'Outcome': ['Improved', 'No Change', 'Worse']},
        title="Age-wise Outcomes for Different Paracetamol Variants",
        labels={'Paracetamol_Variant': 'Paracetamol Variant', 'count': 'Number of Patients'}
    )

    return fig1, fig2

def script10(variant):

    test_smiles = variant 

    # Paracetamol variants with their SMILES
    variants = {
        'Paracetamol_Variant 1': 'CC(=O)NC1=CC=C(C=C1)O',
        'Paracetamol_Variant 2': 'CC(=O)NC1=CCC=C(C=C1)O',
        'Paracetamol_Variant 3': 'CC(=O)NC1=CCC(C=C1)O',
        'Paracetamol_Variant 4': 'CC(=O)NC1=CCC(CC=C1)O'
    }

    # Convert SMILES to RDKit molecules
    test_mol = Chem.MolFromSmiles(test_smiles)
    variant_mols = {key: Chem.MolFromSmiles(smiles) for key, smiles in variants.items()}

    # Compute fingerprints
    test_fp = AllChem.GetMorganFingerprintAsBitVect(test_mol, 2)
    variant_fps = {key: AllChem.GetMorganFingerprintAsBitVect(mol, 2) for key, mol in variant_mols.items()}

    # Calculate Tanimoto similarities
    similarities = {key: DataStructs.TanimotoSimilarity(test_fp, fp) for key, fp in variant_fps.items()}

    # Find the most similar variant
    most_similar_variant = max(similarities, key=similarities.get)

    # Clinical trial outcomes based on the most similar variant
    outcomes = {
        'Paracetamol_Variant 1': 'Improved',
        'Paracetamol_Variant 2': 'No Change',
        'Paracetamol_Variant 3': 'Improved',
        'Paracetamol_Variant 4': 'No Change'
    }

    predicted_outcome = outcomes[most_similar_variant]

    print(f"Most similar paracetamol variant: {most_similar_variant}")
    print(f"Predicted clinical trial outcome: {predicted_outcome}")

    return most_similar_variant, predicted_outcome


def drug_discovery():
    if 'display_clicked' not in st.session_state:
        st.session_state.display_clicked = False

    if 'generate_variants_clicked' not in st.session_state:
        st.session_state.generate_variants_clicked = False

    if 'reconstruct_clicked' not in st.session_state:
        st.session_state.reconstruct_clicked = False

    st.title("Drug Discovery")
    st.selectbox("Generic Name", options=['Paracetamol'])
    st.selectbox('Available Variant', options=['CC(=O)NC1=CC=C(C=C1)O'])
    st.write("Molecular Visualization and Properties")

    display_clicked = st.button('Display')

    if display_clicked:
        st.session_state.display_clicked = True

    if st.session_state.display_clicked:
        viewer = script1()
        text = script2()

        # Create two columns
        col1, col2 = st.columns(2)

        # Display viewer in the first column
        with col1:
            html = viewer._make_html()
            components.html(html, height=250, width=300)

        # Display text in the second column
        with col2:
            st.markdown(text)

        generate_variants_clicked = st.button('Generate Variants')

        if generate_variants_clicked:
            st.session_state.generate_variants_clicked = True

    if st.session_state.generate_variants_clicked:
        variants_text = script3()
        st.write(f'Generated Paracetamol (New Variant) - Molecule  "{variants_text[0]}"')
        st.slider("No of variants", 1,5)
        
        img_bytes4, script4_text = script4()
        # img_bytes5, script5_text = script5()
        img_bytes5 = script5()
        script6_text1, script6_text2 = script6()
        col3, col4 = st.columns(2)
            
        # Display the image in the third column
        with col3:
            st.image(img_bytes4, width=250)

        with col4:
            html = img_bytes5._make_html()
            components.html(html, height=250, width=300)


        col5, col6 = st.columns(2)
        with col5:
            st.markdown(script6_text1)
        with col6:
            st.markdown(script6_text2)

        col7, col8, col9, col10 = st.columns(4)
        with col7:
            mol_wt = st.slider('Mol Wt', 148, 180, 152)
        with col8:
            logp = st.slider('LogP', 1, 8, 1)
        with col9:
            donor = st.slider('No of Hydrogen donors', 1,2,2)
        with col10:
            acceptor = st.slider('No of Hydrogen acceptors',1,2,2)

        reconstruct_clicked = st.button('Reconstruct')

        if reconstruct_clicked:
            st.session_state.reconstruct_clicked = True

    if st.session_state.reconstruct_clicked:
        col11, col12 = st.columns(2)
        output, reconstructed_smiles, properties, model_img7, model_3D7 = script7()
        with col11:
            st.write("Model output:", output)
        with col12:
            st.write("Reconstructed Smiles:", reconstructed_smiles)
        s = ''
        for key, value in properties.items():
            s+='"'+key+'": '+str(value)+',  '
        st.write(s)
        col13, col14 = st.columns(2)
        with col13:
            st.image(model_img7, width=250)
        
        with col14:
            html = model_3D7._make_html()
            components.html(html, height=850, width=300)



def clinical_Trial():
        if 'predict_clicked' not in st.session_state:
            st.session_state.predict_clicked = False
        st.title('Clinical Trial')
        fig1, fig2 = script9()
        gender_data = st.button("Gender wise clinical data")
        if gender_data:
            st.plotly_chart(fig1)
        age_data = st.button("Age wise clinical data")
        if age_data:
            st.plotly_chart(fig2)

        inp = st.text_input("Enter the variant")
        predict_clicked = st.button("Predict Outcome")
        if predict_clicked:
            st.session_state.predict_clicked = True
        if st.session_state.predict_clicked:
            print("entered predict")
            similar_var, outcome = script10(inp)
            st.write(f"Most similar paracetamol variant: {similar_var}")
            st.write(f"Predicted clinical trial outcome: {outcome}")

# Reading the input document
def take_input_document(file, file_type):
    documents = ''
    if file_type == 'pdf':  
        reader = PdfReader(file)
        for page in reader.pages:
            documents += page.extract_text()

        if not documents.strip():
            st.error("No content found in the document.")

        return documents

    elif file_type == 'txt':
        # Load txt documents
        reader = TextLoader(file.name)
        documents = reader.load()[0]

        if not(documents) and not('page_content' in documents):
            st.error("No content found in the document.")
            
        return documents.page_content

    elif file_type == 'csv':
        df = pd.read_csv(file)
        if df.empty:
            st.error("No content found in the document.")
        documents = df.to_string(index=False)
        return documents
    
    elif file_type == 'xlsx' or file_type == 'xls':
        df = pd.read_excel(file)
        if df.empty:
            st.error("No content found in the document.")
        documents = df.to_string(index=False)
        return documents
    
    elif file_type == 'docx':
        doc = Document(file)
        for para in doc.paragraphs:
            documents += para.text + '\n'
        if not documents.strip():
            st.error("No content found in the document.")
        return documents
    
    elif file_type == 'json':
        json_data = json.load(file)
        documents = json.dumps(json_data, indent=2)
        if not documents.strip():
            st.error("No content found in the document.")
        return documents

    else:
        st.error("Unsupported file type")

# Function to process the document and get the LLM response
def process_document_and_get_response(document, prompt):
    # Document Splitting
    chunk_size = 1000
    chunk_overlap = 20

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    split_1 = splitter.split_text(document)
    split_1 = splitter.create_documents(split_1)

    # Load embeddings instructor
    instructor_embeddings = HuggingFaceInstructEmbeddings(
        model_name='hkunlp/instructor-xl', model_kwargs={'device':'cuda'}
    )

    # Implement embeddings
    db = FAISS.from_documents(split_1, instructor_embeddings)

    # Save db
    db.save_local('vector_store/doc')

    # Load db
    loaded_db = FAISS.load_local(
        'vector_store/doc', instructor_embeddings, allow_dangerous_deserialization=True
    )

    # Load LLM
    temperature = 1
    max_length = 100000

    llm_model_name = 'tiiuae/falcon-7b-instruct'
    token = "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"
    
    llm = HuggingFaceHub(
        repo_id=llm_model_name,
        model_kwargs={'temperature': temperature, 'max_length': max_length},
        huggingfacehub_api_token=token
    )

    # Create the chatbot
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type='stuff',
        retriever=loaded_db.as_retriever(),
        return_source_documents=True,
    )

    # # Ask a question
    response = qa({'query': prompt})
    answer = response.get('result').split('Helpful Answer:')[1].strip()
    return answer


def personalized_med_recommendation():
        Personalized_Medication_Recommendation.personalized_med_recommendation()


def insurance_claim():
    insurance_claim_mgmt.insurance_claim()
